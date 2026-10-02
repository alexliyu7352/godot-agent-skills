"""Exercise installation against temporary projects, never the user's project."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/install.py'


class InstallerTests(unittest.TestCase):
    """Check ownership, containment and non-destructive lifecycle behavior."""

    def setUp(self):
        """Make a disposable Godot project with existing user instructions."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'game'
        self.project.mkdir()
        (self.project / 'project.godot').write_text('config_version=5\n')
        (self.project / 'AGENTS.md').write_text('keep agents\n')
        (self.project / 'CLAUDE.md').write_text('keep claude\n')

    def run_installer(self, *args, host='codex', project=None):
        """Run the public installer CLI and retain its exit status."""
        return subprocess.run([sys.executable, str(SCRIPT), '--project', str(project or self.project),
                               '--host', host, *args], capture_output=True, text=True)

    def installed_root(self, host='codex'):
        """Locate the documented project-specific host directory."""
        return self.project / ('.agents' if host == 'codex' else '.claude') / 'skills'

    def test_dry_run_does_not_create_host_directory(self):
        """A preview must perform no project writes."""
        result = self.run_installer('--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / '.agents').exists())

    def test_both_hosts_install_exactly_seven_entries(self):
        """Only allowlisted skill entries may be published to either host."""
        for host in ('codex', 'claude'):
            with self.subTest(host=host):
                result = self.run_installer(host=host)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(list(self.installed_root(host).rglob('SKILL.md'))), 7)
        self.assertEqual((self.project / 'AGENTS.md').read_text(), 'keep agents\n')
        self.assertEqual((self.project / 'CLAUDE.md').read_text(), 'keep claude\n')

    def test_second_install_is_idempotent(self):
        """An unchanged pack must not require a destructive force option."""
        self.assertEqual(self.run_installer().returncode, 0)
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('unchanged', result.stdout)

    def test_unmanaged_collision_blocks_all_writes(self):
        """One conflicting directory must prevent partial installation."""
        conflict = self.installed_root() / 'godot-ui'
        conflict.mkdir(parents=True)
        (conflict / 'SKILL.md').write_text('original')
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((conflict / 'SKILL.md').read_text(), 'original')
        self.assertFalse((self.installed_root() / 'godot-dialogue').exists())

    def test_local_modification_blocks_update_and_remove(self):
        """Updates/removal must preserve user-edited installed content."""
        self.assertEqual(self.run_installer().returncode, 0)
        target = self.installed_root() / 'godot-ui/SKILL.md'
        target.write_text('local edit')
        for option in ('--update', '--uninstall'):
            result = self.run_installer(option)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_text(), 'local edit')

    def test_untracked_file_in_owned_skill_blocks_remove(self):
        """A user's added reference must not be swept away on uninstall."""
        self.assertEqual(self.run_installer().returncode, 0)
        target = self.installed_root() / 'godot-ui/my-notes.md'
        target.write_text('keep this')
        self.assertNotEqual(self.run_installer('--uninstall').returncode, 0)
        self.assertEqual(target.read_text(), 'keep this')

    def test_remove_preserves_unrelated_skills_and_configs(self):
        """Uninstallation owns only this pack's files, never the whole root."""
        self.assertEqual(self.run_installer().returncode, 0)
        other = self.installed_root() / 'my-python-skill'
        other.mkdir()
        (other / 'SKILL.md').write_text('other')
        result = self.run_installer('--uninstall')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((other / 'SKILL.md').read_text(), 'other')
        self.assertEqual((self.project / 'CLAUDE.md').read_text(), 'keep claude\n')
        self.assertEqual(len(list(self.installed_root().glob('godot-*'))), 0)

    def test_missing_project_rejected(self):
        """The installer must not invent a project or install globally."""
        missing = self.project / 'missing'
        self.assertNotEqual(self.run_installer(project=missing).returncode, 0)
        self.assertFalse(missing.exists())

    def test_no_godot_project_rejected(self):
        """A mistaken directory argument must be caught before writes."""
        (self.project / 'project.godot').unlink()
        self.assertNotEqual(self.run_installer().returncode, 0)
        self.assertFalse((self.project / '.agents').exists())

    def test_symlink_host_root_rejected(self):
        """A project path must not redirect installation into another directory."""
        external = Path(self.temp.name) / 'external'
        external.mkdir()
        (self.project / '.agents').symlink_to(external, target_is_directory=True)
        self.assertNotEqual(self.run_installer().returncode, 0)
        self.assertEqual(list(external.iterdir()), [])

    def test_symlink_owned_file_rejected(self):
        """Even same-content symlinks are not owned regular files."""
        self.assertEqual(self.run_installer().returncode, 0)
        target = self.installed_root() / 'godot-ui/SKILL.md'
        external = Path(self.temp.name) / 'external.md'
        external.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(external)
        self.assertNotEqual(self.run_installer('--update').returncode, 0)
        self.assertTrue(target.is_symlink())

    def test_tampered_receipt_path_rejected(self):
        """A receipt must never authorize a path outside the pack's seven roots."""
        self.assertEqual(self.run_installer().returncode, 0)
        receipt = self.installed_root() / '.godot-agent-skills.receipt.json'
        data = json.loads(receipt.read_text())
        data['files']['../../CLAUDE.md'] = '0' * 64
        receipt.write_text(json.dumps(data))
        self.assertNotEqual(self.run_installer('--uninstall').returncode, 0)
        self.assertEqual((self.project / 'CLAUDE.md').read_text(), 'keep claude\n')

    def test_lock_blocks_concurrent_install(self):
        """An existing lock must not be silently stolen or deleted."""
        host_dir = self.project / '.agents'
        host_dir.mkdir()
        lock = host_dir / '.godot-agent-skills.lock'
        lock.write_text('other process')
        self.assertNotEqual(self.run_installer().returncode, 0)
        self.assertEqual(lock.read_text(), 'other process')


if __name__ == '__main__':
    unittest.main()

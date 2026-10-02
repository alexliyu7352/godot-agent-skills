"""Inject filesystem failures into real staged installs to check rollback."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import install as installer
from packlib import file_hash, scan_regular_files


class RollbackTests(unittest.TestCase):
    """Use actual temporary source/project trees with targeted I/O failures."""

    def setUp(self):
        """Create separate source and target roots and redirect only module ROOT."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.source, self.project = base / 'source', base / 'game'
        self.source.mkdir()
        self.project.mkdir()
        (self.project / 'project.godot').write_text('config_version=5\n')
        shutil.copytree(ROOT / 'skills', self.source / 'skills')
        shutil.copyfile(ROOT / 'pack.json', self.source / 'pack.json')
        patch = mock.patch.object(installer, 'ROOT', self.source)
        patch.start()
        self.addCleanup(patch.stop)
        self.destination = self.project / '.agents/skills'

    def invoke(self, *options):
        """Run the public entrypoint while keeping expected failure text out of test logs."""
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            return installer.main(['--project', str(self.project), '--host', 'codex', *options])

    def change_source(self):
        """Make a reviewed mock release by changing content, hash and version together."""
        target = self.source / 'skills/godot-ui/references/layout-localization.md'
        target.write_text(target.read_text() + '\nReviewed update.\n')
        manifest = self.source / 'pack.json'
        data = json.loads(manifest.read_text())
        data['version'] = '0.1.0-preview.2'
        data['skills']['godot-ui']['files']['references/layout-localization.md'] = file_hash(target)
        manifest.write_text(json.dumps(data))

    def test_successful_update_requires_explicit_flag(self):
        """A real managed release update differs from an unchanged repeat install."""
        self.assertEqual(self.invoke(), 0)
        self.change_source()
        old = scan_regular_files(self.destination)
        self.assertNotEqual(self.invoke(), 0)
        self.assertEqual(scan_regular_files(self.destination), old)
        self.assertEqual(self.invoke('--update'), 0)
        self.assertIn('Reviewed update.', (self.destination / 'godot-ui/references/layout-localization.md').read_text())

    def test_failed_fresh_install_rolls_back(self):
        """Failure placing the second directory must remove the first new directory."""
        original_replace = installer.os.replace
        count = 0

        def fail_second(source, target):
            """Simulate an I/O failure on the second commit-phase rename only."""
            nonlocal count
            count += 1
            if count == 2:
                raise OSError('simulated disk failure')
            return original_replace(source, target)

        with mock.patch.object(installer.os, 'replace', side_effect=fail_second):
            self.assertNotEqual(self.invoke(), 0)
        self.assertEqual(scan_regular_files(self.destination), {})
        self.assertFalse((self.project / '.agents' / installer.LOCK).exists())

    def test_failed_update_restores_all_original_bytes(self):
        """One failed placement must restore every previously installed file and receipt."""
        self.assertEqual(self.invoke(), 0)
        before = scan_regular_files(self.destination)
        self.change_source()
        original_replace = installer.os.replace
        count = 0

        def fail_fourth(source, target):
            """Fail once after moving two old directories and one new directory."""
            nonlocal count
            count += 1
            if count == 4:
                raise OSError('simulated replace failure')
            return original_replace(source, target)

        with mock.patch.object(installer.os, 'replace', side_effect=fail_fourth):
            self.assertNotEqual(self.invoke('--update'), 0)
        self.assertEqual(scan_regular_files(self.destination), before)
        self.assertEqual(list((self.project / '.agents').glob('.godot-agent-skills-stage-*')), [])

    def test_incomplete_rollback_preserves_lock_and_backup(self):
        """Unrecoverable I/O failure must retain backup evidence and block another writer."""
        self.assertEqual(self.invoke(), 0)
        self.change_source()
        original_replace = installer.os.replace
        count = 0

        def fail_commit_and_restore(source, target):
            """Simulate persistent disk faults during both update and restoration."""
            nonlocal count
            count += 1
            if count == 4 or Path(source).parent.name == 'old':
                raise OSError('persistent disk fault')
            return original_replace(source, target)

        with mock.patch.object(installer.os, 'replace', side_effect=fail_commit_and_restore):
            self.assertNotEqual(self.invoke('--update'), 0)
        self.assertTrue((self.project / '.agents' / installer.LOCK).exists())
        self.assertTrue(list((self.project / '.agents').glob('.godot-agent-skills-stage-*/old/*')))

    def test_changed_source_without_hash_update_is_refused(self):
        """Unreviewed source changes must not be installed even with --update."""
        (self.source / 'skills/godot-ui/SKILL.md').write_text('tampered')
        self.assertNotEqual(self.invoke(), 0)
        self.assertFalse((self.project / '.agents').exists())


if __name__ == '__main__':
    unittest.main()

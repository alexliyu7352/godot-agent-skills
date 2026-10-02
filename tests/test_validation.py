"""Test the package validator with actual malformed temporary source trees."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import packlib


class ValidationTests(unittest.TestCase):
    """Mutations must fail validation rather than entering an installable pack."""

    def setUp(self):
        """Copy only validation inputs into a disposable directory."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'skills', self.root / 'skills')
        shutil.copyfile(ROOT / 'pack.json', self.root / 'pack.json')

    def test_valid_manifest(self):
        """A clean reviewed allowlist should match every installable byte."""
        self.assertEqual(packlib.load_manifest(self.root)['id'], 'godot-agent-skills')

    def test_added_skill_refused(self):
        """A hidden legacy router cannot silently enter publication."""
        extra = self.root / 'skills/old-router'
        extra.mkdir()
        (extra / 'SKILL.md').write_text('unwanted')
        with self.assertRaises(ValueError):
            packlib.load_manifest(self.root)

    def test_changed_reference_refused(self):
        """Reference content changes require a reviewed manifest update."""
        target = self.root / 'skills/godot-ui/references/input-visual.md'
        target.write_text('changed')
        with self.assertRaises(ValueError):
            packlib.load_manifest(self.root)

    def test_traversal_and_normalized_paths_refused(self):
        """Traversal and ambiguous path forms are rejected before normalization."""
        for value in ('../x', 'a/../b', '/absolute', 'a//b', './x', 'a\\b', 'C:/x', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                packlib.safe_relative(value)

    def test_duplicate_json_key_refused(self):
        """Duplicate JSON keys must not override an earlier allowlist entry."""
        target = self.root / 'duplicate.json'
        target.write_text('{"id":"good","id":"bad"}')
        with self.assertRaises(ValueError):
            packlib.read_json(target)

    def test_symlink_source_refused(self):
        """Even an allowlisted filename may not redirect to external content."""
        target = self.root / 'skills/godot-ui/SKILL.md'
        original = target.read_text()
        target.unlink()
        external = self.root / 'external.md'
        external.write_text(original)
        target.symlink_to(external)
        with self.assertRaises(ValueError):
            packlib.load_manifest(self.root)

    def test_validator_command_exists_and_passes(self):
        """The public validator must actually validate the release tree."""
        result = subprocess.run([sys.executable, str(ROOT / 'tools/validate.py')],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('static_validation_passed', result.stdout)


if __name__ == '__main__':
    unittest.main()

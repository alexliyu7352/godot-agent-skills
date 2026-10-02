"""Check the release boundary; these are static packaging tests, not agent evals."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    'godot-code-scenes', 'godot-data-state', 'godot-ui', 'godot-dialogue',
    'godot-save-load', 'godot-debugging', 'godot-verification',
}

class DistributionTests(unittest.TestCase):
    """Keep the discoverable surface at the seven approved entries."""

    def test_exact_seven_entries(self):
        """An extra archived/router skill must make this test fail."""
        paths = list((ROOT / 'skills').rglob('SKILL.md'))
        self.assertEqual({p.parent.name for p in paths}, EXPECTED)
        self.assertEqual(len(paths), 7)

    def test_manifest_exists(self):
        """Installation must use an explicit release allowlist, not recursive copy."""
        self.assertTrue((ROOT / 'pack.json').is_file())

    def test_sources_are_pinned(self):
        """Upstream sources must be recoverable by a full immutable commit SHA."""
        self.assertTrue((ROOT / 'sources.lock.json').is_file())
        data = json.loads((ROOT / 'sources.lock.json').read_text())
        self.assertEqual(len(data['upstreams']), 3)
        for upstream in data['upstreams']:
            self.assertRegex(upstream['commit'], r'^[0-9a-f]{40}$')

if __name__ == '__main__':
    unittest.main()

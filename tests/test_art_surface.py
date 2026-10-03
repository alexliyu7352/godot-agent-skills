"""Mechanical publication guards; these tests do not grade art or model behavior."""
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from packlib import load_manifest

ART_REFERENCES = {
    'godot-ui': ['art-direction.md', 'asset-production.md', 'game-presentation.md'],
    'godot-code-scenes': ['scene-composition.md'],
    'godot-verification': ['art-review.md'],
}


class ArtSurfaceTests(unittest.TestCase):
    """Keep art knowledge installable without adding a new automatic entry."""

    def test_art_references_are_published_and_reachable(self):
        """References must not exist only in development docs outside the package."""
        manifest = load_manifest(ROOT)
        for skill, names in ART_REFERENCES.items():
            entry = (ROOT / 'skills' / skill / 'SKILL.md').read_text()
            for name in names:
                with self.subTest(skill=skill, name=name):
                    self.assertIn('references/' + name, manifest['skills'][skill]['files'])
                    self.assertIn('(references/' + name + ')', entry)

    def test_art_source_maps_to_fixed_upstream(self):
        """Actual newly consumed art sources retain their upstream provenance."""
        mappings = json.loads((ROOT / 'sources.lock.json').read_text())['skills']
        for skill in ART_REFERENCES:
            paths = {item['path'] for item in mappings[skill]['inputs']}
            self.assertIn('skills/disciplines/create-game-assets/SKILL.md', paths)

    def test_new_art_cases_keep_real_host_status_unexecuted(self):
        """Defining expectations must not change NOT_RUN into a fake success."""
        cases = [json.loads(line) for line in (ROOT / 'evals/cases.jsonl').read_text().splitlines() if line.strip()]
        ids = {case['id'] for case in cases}
        self.assertTrue({'art-new-room', 'art-cohesive-family', 'art-local-margin', 'art-not-web'} <= ids)
        state = json.loads((ROOT / 'evals/status.json').read_text())
        self.assertEqual(state['cases_defined'], len(cases))
        self.assertEqual(state['status'], 'NOT_RUN')

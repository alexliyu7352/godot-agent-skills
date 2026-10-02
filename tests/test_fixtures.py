"""Check fixture preparation and trigger-contract text, not agent behavior."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_fixtures
import validate


class FixtureTests(unittest.TestCase):
    """Preparers must preserve source bytes, expose real faults and never overwrite."""

    def test_all_faults_have_exact_anchors_and_leave_sources_unchanged(self):
        """Prepared bad variants differ at the intended point without changing the source."""
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            check_fixtures.prepare(base / 'good')
            for variant, (file, old, new, _, _) in check_fixtures.MUTATIONS.items():
                with self.subTest(variant=variant):
                    check_fixtures.prepare(base / variant, variant)
                    before = (base / 'good/examples' / file).read_text()
                    after = (base / variant / 'examples' / file).read_text()
                    self.assertEqual(after, before.replace(old, new))
                    source = ROOT / 'skills' / check_fixtures.EXAMPLES[file] / 'references' / file
                    self.assertEqual(source.read_text(), before)
            with self.assertRaises(ValueError):
                check_fixtures.prepare(base / 'good')

    def test_prepare_cli_needs_no_engine_or_model(self):
        """Offline fixture construction is useful even before a host can execute it."""
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'game'
            result = subprocess.run([sys.executable, str(ROOT / 'tools/check_fixtures.py'),
                                     '--prepare-only', '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((out / 'project.godot').is_file())
            self.assertEqual(list(out.rglob('SKILL.md')), [])

    def test_metadata_no_longer_routes_all_visible_edits_to_verification(self):
        """Guard the specific reviewed broad phrase; this is not a semantic evaluator."""
        skill = (ROOT / 'skills/godot-verification/SKILL.md').read_text()
        self.assertNotIn('and player-visible behavior', validate.frontmatter(skill)['description'])
        code = validate.frontmatter((ROOT / 'skills/godot-code-scenes/SKILL.md').read_text())
        self.assertIn('.gd scripts', code['description'])
        cases = [json.loads(row) for row in (ROOT / 'evals/cases.jsonl').read_text().splitlines()]
        case = next(row for row in cases if row['id'] == 'ui-local-theme')
        self.assertEqual(case['allowed_pack_skills'], ['godot-ui'])


if __name__ == '__main__':
    unittest.main()

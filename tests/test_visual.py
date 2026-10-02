"""Test visual-fixture preparation and result grading, not screenshot aesthetics."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VisualTests(unittest.TestCase):
    """The real renderer path must remain separate from headless contract checks."""

    def module(self):
        """Load the visual tool after checking the intended deliverable exists."""
        path = ROOT / 'tools/check_visual.py'
        self.assertTrue(path.is_file(), 'actual rendering runner is missing')
        spec = importlib.util.spec_from_file_location('check_visual', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_prepare_has_actual_renderer_and_only_selected_examples(self):
        """Export a self-contained render project without installing an agent skill."""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'project'
            module.prepare_visual(target)
            self.assertTrue((target / 'capture.gd').is_file())
            self.assertEqual({p.name for p in (target / 'examples').iterdir()},
                             {'choice_routes.gd', 'local_theme.gd'})
            self.assertEqual(list(target.rglob('SKILL.md')), [])
            with self.assertRaises(ValueError):
                module.prepare_visual(target)

    def test_real_render_command_cannot_silently_be_headless(self):
        """Visual runs require an X11 display and a real compatibility renderer."""
        command = self.module().engine_command('/bin/godot', Path('/tmp/project'), 800, 600)
        self.assertNotIn('--headless', command)
        self.assertIn('x11', command)
        self.assertIn('gl_compatibility', command)
        self.assertIn('800x600', command)

    def test_faults_change_only_disposable_copies(self):
        """Each injected UI failure must target a known unique source fragment."""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module.prepare_visual(root / 'baseline')
            original = (root / 'baseline/ui_fixture.gd').read_bytes()
            for variant in module.FAULTS:
                module.prepare_visual(root / variant, variant)
                self.assertNotEqual((root / variant / 'ui_fixture.gd').read_bytes(), original)
            self.assertEqual((ROOT / 'evals/visual/ui_fixture.gd').read_bytes(), original)

    def test_error_exit_without_target_assertion_is_not_mutation_success(self):
        """Missing images and parser crashes must not count as caught UI regressions."""
        module = self.module()
        self.assertFalse(module.matches_expected(1, '', 'SCRIPT ERROR: parse failed',
                                                {'capture_complete': False}, 'text-clipping'))
        self.assertFalse(module.matches_expected(0, 'VISUAL_DONE', '',
                                                {'capture_complete': True}, 'text-clipping'))
        self.assertFalse(module.matches_expected(0, 'VISUAL_DONE', '',
                                                {'capture_complete': False}, 'baseline'))


if __name__ == '__main__':
    unittest.main()

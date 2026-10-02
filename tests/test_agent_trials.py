"""Verify trial preparation without simulating model behavior or declaring success."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AgentTrialTests(unittest.TestCase):
    """Control and treatment differ only in installed skills, never in solution hints."""

    def module(self):
        """Load the missing-to-present preparer for test-first development."""
        path = ROOT / 'tools/prepare_agent_trial.py'
        self.assertTrue(path.is_file(), 'clean agent trial preparer is missing')
        spec = importlib.util.spec_from_file_location('prepare_agent_trial', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_same_fault_and_prompt_for_both_conditions_and_hosts(self):
        """Treatment may add skills but must not silently fix the starting game."""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            for host in ['codex', 'claude']:
                base = Path(directory) / host
                control = module.prepare_trial(base / 'control', 'dialogue-empty', host, False)
                treated = module.prepare_trial(base / 'treated', 'dialogue-empty', host, True)
                self.assertEqual(control['project_sha256'], treated['project_sha256'])
                self.assertEqual(control['task_sha256'], treated['task_sha256'])
                self.assertEqual(control['status'], 'NOT_RUN')
                self.assertEqual(treated['status'], 'NOT_RUN')
                self.assertEqual(len(list((base / 'control/project').rglob('SKILL.md'))), 0)
                self.assertEqual(len(list((base / 'treated/project').rglob('SKILL.md'))), 7)

    def test_workspace_does_not_contain_grader_or_mutation_description(self):
        """Trusted checks and failure recipes stay outside the editable task project."""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'trial'
            module.prepare_trial(root, 'scene-owner', 'codex', False)
            self.assertFalse((root / 'project/checks.gd').exists())
            self.assertFalse((root / 'project/README.md').exists())
            self.assertTrue((root / 'grader/checks.gd').is_file())
            prompt = (root / 'task.txt').read_text()
            self.assertNotIn('godot-code-scenes', prompt)
            self.assertNotIn('MUTATIONS', prompt)

    def test_all_variants_exist_and_original_repo_is_untouched(self):
        """Every existing contract fault is exportable, with no extra network runner."""
        module = self.module()
        before = (ROOT / 'pack.json').read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            for variant in module.TASKS:
                root = Path(directory) / variant
                result = module.prepare_trial(root, variant, 'codex', False)
                self.assertTrue(result['project_sha256'])
                self.assertEqual(json.loads((root / 'trial.json').read_text())['status'], 'NOT_RUN')
        self.assertEqual((ROOT / 'pack.json').read_bytes(), before)

    def test_existing_output_is_not_reused(self):
        """Old logs or changed source cannot silently masquerade as a new trial."""
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'trial'
            module.prepare_trial(root, 'future-save', 'codex', False)
            with self.assertRaises(ValueError):
                module.prepare_trial(root, 'future-save', 'codex', False)


if __name__ == '__main__':
    unittest.main()

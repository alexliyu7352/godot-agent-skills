"""Mechanical publication guards; these tests do not grade art or model behavior."""
from pathlib import Path
import json
import copy
import math
import tempfile
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

    def test_art_cases_match_result_record(self):
        """Defined cases and host status must agree without fixing a permanent status."""
        cases = [json.loads(line) for line in (ROOT / 'evals/cases.jsonl').read_text().splitlines() if line.strip()]
        ids = {case['id'] for case in cases}
        self.assertTrue({'art-new-room', 'art-cohesive-family', 'art-local-margin', 'art-not-web'} <= ids)
        state = json.loads((ROOT / 'evals/status.json').read_text())
        self.assertEqual(state['cases_defined'], len(cases))
        self.check_status_evidence(state, ROOT / 'evals')

    def check_status_evidence(self, state: dict, evidence_root: Path) -> None:
        """Check status/evidence consistency only; file existence cannot prove a run."""
        statuses = {'NOT_RUN', 'PARTIAL', 'COMPLETED'}
        self.assertIn(state.get('status'), statuses)
        hosts = state.get('hosts')
        self.assertIsInstance(hosts, dict)
        self.assertTrue(hosts)
        host_states = []
        for host in hosts.values():
            self.assertIsInstance(host, dict)
            self.assertIn(host.get('status'), statuses)
            host_states.append(host['status'])
            evidence = host.get('evidence', [])
            self.assertIsInstance(evidence, list)
            if host['status'] == 'NOT_RUN':
                self.assertEqual(evidence, [])
                continue
            for field in ['version', 'model']:
                self.assertIsInstance(host.get(field), str)
                self.assertTrue(host[field].strip())
            self.assertTrue(evidence, 'reported host runs need evidence references')
            for relative in evidence:
                self.assertIsInstance(relative, str)
                self.assertTrue(relative.strip())
                path = Path(relative)
                self.assertFalse(path.is_absolute())
                target = (evidence_root / path).resolve()
                self.assertTrue(target.is_relative_to(evidence_root.resolve()))
                self.assertTrue(target.is_file(), f'missing evidence: {relative}')
                self.assertGreater(target.stat().st_size, 0)
        if state['status'] == 'NOT_RUN':
            self.assertTrue(all(item == 'NOT_RUN' for item in host_states))
        elif state['status'] == 'COMPLETED':
            self.assertTrue(all(item == 'COMPLETED' for item in host_states))
        else:
            self.assertTrue(any(item != 'NOT_RUN' for item in host_states))
        for key in ['automatic_trigger_accuracy', 'task_success_rate']:
            value = state.get(key)
            if state['status'] == 'NOT_RUN':
                self.assertIsNone(value)
            elif value is not None:
                self.assertIn(type(value), (int, float))
                self.assertTrue(math.isfinite(value) and 0 <= value <= 1)

    def test_status_allows_evidenced_completion(self):
        """Synthetic records may transition when references exist, without real model claims."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'report.md').write_text('Synthetic metadata fixture; not an agent run.\n')
            host = {'status': 'COMPLETED', 'version': 'synthetic', 'model': 'synthetic',
                    'evidence': ['report.md']}
            state = {'status': 'COMPLETED', 'hosts': {'codex': host},
                     'automatic_trigger_accuracy': 0.5, 'task_success_rate': None}
            self.check_status_evidence(state, root)
            state['status'] = 'PARTIAL'
            state['hosts']['claude-code'] = {'status': 'NOT_RUN'}
            self.check_status_evidence(state, root)

    def test_status_rejects_unsubstantiated_completion(self):
        """Missing files, empty evidence and inconsistent host declarations must fail."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'report.md').write_text('Synthetic metadata fixture; not an agent run.\n')
            (root / 'empty.md').touch()
            valid = {'status': 'COMPLETED', 'hosts': {'codex': {
                'status': 'COMPLETED', 'version': 'synthetic', 'model': 'synthetic',
                'evidence': ['report.md']}}}
            for evidence in [[], ['missing.md'], ['empty.md'], ['/absolute.md']]:
                state = copy.deepcopy(valid)
                state['hosts']['codex']['evidence'] = evidence
                with self.subTest(evidence=evidence), self.assertRaises(AssertionError):
                    self.check_status_evidence(state, root)
            for model in [None, '']:
                state = copy.deepcopy(valid)
                state['hosts']['codex']['model'] = model
                with self.subTest(model=model), self.assertRaises(AssertionError):
                    self.check_status_evidence(state, root)
            state = copy.deepcopy(valid)
            state['hosts']['codex'] = {'status': 'NOT_RUN'}
            with self.assertRaises(AssertionError):
                self.check_status_evidence(state, root)

    def test_not_run_cannot_report_metrics_or_runs(self):
        """Current unavailable hosts stay truthful without preventing future evidence."""
        state = {'status': 'NOT_RUN', 'hosts': {'codex': {'status': 'NOT_RUN'}},
                 'automatic_trigger_accuracy': None, 'task_success_rate': None}
        self.check_status_evidence(state, ROOT / 'evals')
        for key in ['automatic_trigger_accuracy', 'task_success_rate']:
            bad = copy.deepcopy(state)
            bad[key] = 1.0
            with self.subTest(key=key), self.assertRaises(AssertionError):
                self.check_status_evidence(bad, ROOT / 'evals')
        state['hosts']['codex']['evidence'] = ['old-report.md']
        with self.assertRaises(AssertionError):
            self.check_status_evidence(state, ROOT / 'evals')

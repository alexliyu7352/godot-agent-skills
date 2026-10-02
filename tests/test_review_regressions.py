"""Regression contracts from review R1-R3 and R7-R8; no model claims."""
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import install as installer
import validate
from packlib import file_hash
RUNNER = ROOT / 'skills/godot-verification/scripts/run_check.py'


class ReviewRegressions(unittest.TestCase):
    """Use real files/processes and inject failures only at reviewed boundaries."""

    def setUp(self):
        """Allocate a disposable project outside the source package."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'game'
        self.project.mkdir()
        (self.project / 'project.godot').write_text('config_version=5\n')

    def invoke(self, *options):
        """Call the public installer and retain structured and human reports."""
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = installer.main(['--host', 'codex', '--project', str(self.project), *options])
        return code, out.getvalue(), err.getvalue()

    def test_cleanup_failure_after_commit_has_truthful_status(self):
        """Install, update and remove must report committed changes, not refusal."""
        source = self.base / 'source'
        shutil.copytree(ROOT / 'skills', source / 'skills')
        shutil.copyfile(ROOT / 'pack.json', source / 'pack.json')
        original = shutil.rmtree

        def fail_cleanup(path, *args, **kwargs):
            """Fail only disposal of the transaction staging directory."""
            if Path(path).name.startswith('.godot-agent-skills-stage-'):
                raise PermissionError('cleanup denied by regression test')
            return original(path, *args, **kwargs)

        with patch.object(installer, 'ROOT', source):
            for options, action in [((), 'install'), (('--update',), 'update'), (('--uninstall',), 'uninstall')]:
                if action == 'update':
                    p = source / 'skills/godot-ui/references/layout-localization.md'
                    p.write_text(p.read_text() + '\nReviewed new release.\n')
                    data = json.loads((source / 'pack.json').read_text())
                    data['version'] += '-test'
                    data['skills']['godot-ui']['files']['references/layout-localization.md'] = file_hash(p)
                    (source / 'pack.json').write_text(json.dumps(data))
                with self.subTest(action=action), patch.object(installer.shutil, 'rmtree', side_effect=fail_cleanup):
                    code, out, err = self.invoke(*options)
                    self.assertEqual(code, 0, err)
                    report = json.loads(out.splitlines()[0])
                    self.assertEqual(report['status'], 'committed_cleanup_pending')
                    self.assertEqual(report['action'], action)
                    self.assertTrue(Path(report['cleanup_path']).exists())
                    self.assertNotIn('INSTALL REFUSED', err)
                    destination = self.project / '.agents/skills'
                    self.assertEqual(len(list(destination.rglob('SKILL.md'))), 0 if action == 'uninstall' else 7)
                    self.assertEqual((destination / installer.RECEIPT).exists(), action != 'uninstall')

    @unittest.skipUnless(os.name == 'posix', 'POSIX group cleanup contract')
    def test_late_worker_error_is_captured_before_report(self):
        """Normal launcher exit is insufficient while inherited streams remain open."""
        child = "import sys,time; time.sleep(0.35); print('SCRIPT ERROR: late failure',file=sys.stderr,flush=True)"
        parent = f"import subprocess,sys; subprocess.Popen([sys.executable,'-c',{child!r}]); print('EARLY_DONE',flush=True)"
        evidence = self.base / 'late'
        result = subprocess.run([sys.executable, str(RUNNER), '--out', str(evidence), '--timeout', '4',
                                 '--require-text', 'EARLY_DONE', '--', sys.executable, '-c', parent],
                                capture_output=True, text=True, timeout=10)
        report = json.loads((evidence / 'report.json').read_text())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(report['error_count'], 1)
        self.assertTrue(report['streams_complete'])
        for name, entry in report['logs'].items():
            self.assertEqual(entry['sha256'], file_hash(evidence / f'{name}.log'))

    @unittest.skipUnless(os.name == 'posix', 'POSIX group cleanup contract')
    def test_worker_holding_streams_open_times_out(self):
        """A departed launcher cannot bypass the total deadline for open writers."""
        child = "import time; time.sleep(30)"
        parent = f"import subprocess,sys; subprocess.Popen([sys.executable,'-c',{child!r}]); print('DONE',flush=True)"
        evidence = self.base / 'held'
        result = subprocess.run([sys.executable, str(RUNNER), '--out', str(evidence), '--timeout', '0.4',
                                 '--', sys.executable, '-c', parent], capture_output=True, text=True, timeout=8)
        report = json.loads((evidence / 'report.json').read_text())
        self.assertEqual(result.returncode, 124)
        self.assertEqual(report['status'], 'timed_out')
        before = (evidence / 'stdout.log').read_bytes()
        time.sleep(0.1)
        self.assertEqual(before, (evidence / 'stdout.log').read_bytes())

    @unittest.skipUnless(os.name == 'posix', 'Detached process probe requires POSIX')
    def test_escaped_writer_is_incomplete_and_cannot_mutate_logs(self):
        """An unkillable-by-group writer must not pass or own a captured log file."""
        pidfile = self.base / 'escaped.pid'
        child = "import os,time,pathlib; pathlib.Path(%r).write_text(str(os.getpid())); time.sleep(20)" % str(pidfile)
        parent = f"import subprocess,sys; subprocess.Popen([sys.executable,'-c',{child!r}], start_new_session=True)"
        evidence = self.base / 'escaped'
        try:
            result = subprocess.run([sys.executable, str(RUNNER), '--out', str(evidence), '--timeout', '1',
                                     '--', sys.executable, '-c', parent], capture_output=True, text=True, timeout=8)
            self.assertEqual(result.returncode, 124, result.stderr)
            report = json.loads((evidence / 'report.json').read_text())
            self.assertFalse(report['streams_complete'])
            self.assertEqual(report['logs']['stderr']['sha256'], file_hash(evidence / 'stderr.log'))
        finally:
            if pidfile.exists():
                try:
                    os.kill(int(pidfile.read_text()), 9)
                except ProcessLookupError:
                    pass

    def test_rollback_and_cleanup_failures_are_distinguished(self):
        """A restored target with disposable leftovers is rolled_back, not committed."""
        replace = installer.os.replace
        remove = installer.shutil.rmtree
        calls = 0

        def fail_second(source, target):
            """Fail one commit-phase placement; allow actual rollback to work."""
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('placement failed')
            return replace(source, target)

        def fail_cleanup(path, *args, **kwargs):
            """Fail only post-rollback staging disposal, not installed state restoration."""
            if Path(path).name.startswith('.godot-agent-skills-stage-'):
                raise PermissionError('leftover cleanup denied')
            return remove(path, *args, **kwargs)

        with patch.object(installer.os, 'replace', side_effect=fail_second), \
             patch.object(installer.shutil, 'rmtree', side_effect=fail_cleanup):
            code, _, err = self.invoke()
        self.assertEqual(code, 2)
        report = json.loads(err.strip())
        self.assertEqual(report['status'], 'rolled_back')
        self.assertTrue(Path(report['cleanup_path']).exists())
        self.assertFalse(list((self.project / '.agents/skills').rglob('SKILL.md')))
        self.assertFalse((self.project / '.agents' / installer.LOCK).exists())

    def test_real_git_autocrlf_checkout_remains_installable(self):
        """A clean Git checkout must preserve allowlisted bytes under autocrlf=true."""
        source, checkout = self.base / 'snapshot', self.base / 'checkout'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        commands = [ ['git', 'init', '-q', str(source)],
                     ['git', '-C', str(source), '-c', 'core.autocrlf=false', 'add', '.'],
                     ['git', '-C', str(source), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid',
                      'commit', '-qm', 'fixture'],
                     ['git', 'clone', '-q', '--config', 'core.autocrlf=true', str(source), str(checkout)] ]
        for command in commands:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(checkout / 'tools/validate.py')],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(checkout / 'tools/install.py'), '--host', 'codex',
                                 '--project', str(self.project), '--dry-run'],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(subprocess.check_output(['git', '-C', str(checkout), 'status', '--porcelain']), b'')

    def test_invalid_case_contracts_are_rejected(self):
        """Reject negative allowlists, unknown kinds and malformed rubrics/candidates."""
        source = (ROOT / 'evals/cases.jsonl').read_text(encoding='utf-8')
        mutations = [('negative', 'allowed_pack_skills', ['godot-ui']),
                     ('positive', 'kind', 'unknown'), ('positive', 'expected_primary_any', []),
                     ('positive', 'checks', ['']), ('positive', 'checks', [123]),
                     ('positive', 'allowed_pack_skills', 'godot-ui')]
        for kind, field, value in mutations:
            rows = [json.loads(line) for line in source.splitlines() if line.strip()]
            target = next(row for row in rows if row['kind'] == kind)
            target[field] = value
            path = self.base / 'cases.jsonl'
            path.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                validate.check_cases(path)

    def test_invalid_source_references_are_rejected(self):
        """Check source ID uniqueness, immutable URL consistency and safe paths offline."""
        raw = (ROOT / 'sources.lock.json').read_text(encoding='utf-8')
        source = self.base / 'provenance'
        shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        for mutation in ('unknown', 'duplicate', 'url', 'path', 'repository', 'commit'):
            lock = json.loads(raw)
            item = lock['skills']['godot-ui']['inputs'][0]
            if mutation == 'unknown':
                item['upstream'] = 'NONEXISTENT-UPSTREAM'
            elif mutation == 'duplicate':
                lock['upstreams'][1]['id'] = lock['upstreams'][0]['id']
            elif mutation == 'url':
                item['url'] = item['url'].replace('/blob/', '/tree/')
            elif mutation == 'path':
                item['path'] = '../elsewhere.md'
            elif mutation == 'repository':
                lock['upstreams'][0]['repository'] = ''
            else:
                lock['upstreams'][0]['commit'] = 'main'
            (source / 'sources.lock.json').write_text(json.dumps(lock), encoding='utf-8')
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate.validate(source)


if __name__ == '__main__':
    unittest.main()

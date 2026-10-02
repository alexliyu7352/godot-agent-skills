"""Exercise real subprocesses to verify the evidence wrapper's error handling."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/godot-verification/scripts/run_check.py'


class RunnerTests(unittest.TestCase):
    """These tests exercise Python processes, not the Godot engine or an agent."""

    def setUp(self):
        """Create a fresh evidence path for every test."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / 'evidence'

    def invoke(self, program, *options):
        """Run a small real process through the public wrapper CLI."""
        return subprocess.run([sys.executable, str(SCRIPT), '--out', str(self.out),
                               '--timeout', '2', *options, '--', sys.executable, '-c', program],
                              capture_output=True, text=True)

    def report(self):
        """Read machine-readable observations from this test run."""
        return json.loads((self.out / 'report.json').read_text())

    def test_success_with_marker(self):
        """Exit zero and a required completion marker satisfy the command contract."""
        result = self.invoke("print('CHECK_DONE')", '--require-text', 'CHECK_DONE')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.report()['status'], 'command_passed')
        self.assertFalse(self.report()['proves_game_quality'])

    def test_nonzero_fails_even_with_marker(self):
        """A printed success string must not override a failing exit code."""
        result = self.invoke("print('CHECK_DONE'); raise SystemExit(7)", '--require-text', 'CHECK_DONE')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.report()['returncode'], 7)

    def test_stderr_error_fails_even_exit_zero(self):
        """Godot-style errors on stderr must survive an otherwise successful exit."""
        result = self.invoke("import sys; print('SCRIPT ERROR: bad call', file=sys.stderr)")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.report()['error_lines'])

    def test_assert_fail_stdout(self):
        """The wrapper recognizes explicit failing assertions in stdout."""
        result = self.invoke("print('ASSERT FAIL: currency')")
        self.assertNotEqual(result.returncode, 0)

    def test_ansi_error_recognized(self):
        """Terminal coloring must not hide the error prefix."""
        result = self.invoke("print('\\x1b[31mERROR: bad resource\\x1b[0m')")
        self.assertNotEqual(result.returncode, 0)

    def test_zero_errors_is_not_error(self):
        """Successful summaries containing the word errors are not false positives."""
        result = self.invoke("print('0 errors, 8 tests passed')")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_marker_fails(self):
        """A test that exits early cannot pass only because its exit code is zero."""
        result = self.invoke("print('started')", '--require-text', 'CHECK_DONE')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.report()['missing_markers'], ['CHECK_DONE'])

    def test_marker_in_stderr_is_accepted(self):
        """Both output streams are included in the completion evidence."""
        result = self.invoke("import sys; print('CHECK_DONE', file=sys.stderr)", '--require-text', 'CHECK_DONE')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_timeout_records_failure(self):
        """Hung checks must terminate and cannot be reported as passing."""
        result = self.invoke("import time; time.sleep(10)", '--timeout', '0.1')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.report()['timed_out'])

    def test_existing_evidence_directory_refused(self):
        """Old logs must not be mistaken for a fresh successful verification."""
        self.out.mkdir()
        (self.out / 'report.json').write_text('old')
        result = self.invoke("print('new')")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.out / 'report.json').read_text(), 'old')

    def test_missing_command(self):
        """An unavailable executable must produce a truthful launch error report."""
        result = subprocess.run([sys.executable, str(SCRIPT), '--out', str(self.out), '--',
                                 '/definitely/missing/godot'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.report()['status'], 'launch_failed')

    def test_literal_command_arguments_no_shell(self):
        """Command metacharacters remain data unless the caller explicitly runs a shell."""
        result = self.invoke("import sys; print(sys.argv)")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.report()['command'][0], sys.executable)

    def test_large_output_kept_on_disk(self):
        """Logs are preserved without serializing the entire output into report JSON."""
        result = self.invoke("print('x' * 300000); print('CHECK_DONE')", '--require-text', 'CHECK_DONE')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater((self.out / 'stdout.log').stat().st_size, 300000)
        self.assertLess((self.out / 'report.json').stat().st_size, 12000)


if __name__ == '__main__':
    unittest.main()

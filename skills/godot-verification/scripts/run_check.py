#!/usr/bin/env python3
"""Capture a command's fresh evidence; never equate exit zero with game quality.

Python 3.10+, standard library only. No network, shell expansion, model selection,
Godot installation or project edits are performed by this wrapper. The explicitly
supplied command can have its own side effects and is NOT sandboxed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
ERROR_PREFIX = re.compile(r'^\s*(?:SCRIPT ERROR:|ERROR:|ASSERT\s+FAIL(?:\b|:)|\[FAIL\])')
CHUNK = 65536
MAX_ERROR_SAMPLES = 100


def utc_now() -> str:
    """Return an explicit UTC timestamp for evidence provenance."""
    return datetime.now(timezone.utc).isoformat()


def digest(path: Path) -> str:
    """Hash a log incrementally without copying its contents into memory."""
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(CHUNK), b''):
            value.update(data)
    return value.hexdigest()


def scan_log(path: Path, markers: list[str]) -> tuple[list[str], int, set[str]]:
    """Recognize common error prefixes and literal markers using bounded reads.

    The matcher is deliberately a heuristic, not a Godot/test-protocol parser.
    Logs are preserved in full even when only bounded samples enter the report.
    """
    samples: list[str] = []
    error_count = 0
    seen: set[str] = set()
    encoded = {marker: marker.encode('utf-8') for marker in markers}
    overlap_size = max([len(value) for value in encoded.values()] + [1]) - 1
    tail = b''
    start_of_line = True
    with path.open('rb') as stream:
        while data := stream.readline(CHUNK):
            combined = tail + data
            for marker, value in encoded.items():
                if value in combined:
                    seen.add(marker)
            tail = combined[-overlap_size:] if overlap_size else b''
            if start_of_line:
                text = ANSI.sub('', data[:4096].decode('utf-8', errors='replace')).rstrip()
                if ERROR_PREFIX.search(text):
                    error_count += 1
                    if len(samples) < MAX_ERROR_SAMPLES:
                        samples.append(text[:1000])
            start_of_line = data.endswith(b'\n')
    return samples, error_count, seen


def stop_process(process: subprocess.Popen[bytes]) -> None:
    """Stop this command's POSIX group, or just its direct child on Windows."""
    if os.name == 'posix':
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=0.5)
        except subprocess.TimeoutExpired:
            pass
        # Also kill surviving group members if the group leader already exited.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.kill()
    process.wait()


def execute(command: list[str], cwd: Path, timeout: float, out: Path,
            markers: list[str]) -> tuple[dict, int]:
    """Run one explicit command and write logs plus an observation report."""
    out.mkdir(parents=True, exist_ok=False)
    started = utc_now()
    before = time.monotonic()
    timed_out = False
    interrupted = False
    launch_error = None
    returncode = None
    stdout_path, stderr_path = out / 'stdout.log', out / 'stderr.log'
    with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
        try:
            process = subprocess.Popen(command, cwd=str(cwd), stdout=stdout, stderr=stderr,
                                       stdin=subprocess.DEVNULL, start_new_session=(os.name == 'posix'))
            try:
                returncode = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                stop_process(process)
                returncode = process.returncode
            except KeyboardInterrupt:
                interrupted = True
                stop_process(process)
                returncode = process.returncode
        except OSError as exc:
            launch_error = f'{type(exc).__name__}: {exc}'

    error_lines: list[dict] = []
    error_count = 0
    seen: set[str] = set()
    for label, path in [('stdout', stdout_path), ('stderr', stderr_path)]:
        samples, count, found = scan_log(path, markers)
        error_lines.extend({'stream': label, 'text': text} for text in samples)
        error_count += count
        seen.update(found)
    missing = [marker for marker in markers if marker not in seen]
    passed = not (launch_error or timed_out or interrupted or returncode != 0 or error_count or missing)
    status = 'command_passed' if passed else 'command_failed'
    if launch_error:
        status = 'launch_failed'
    elif timed_out:
        status = 'timed_out'
    elif interrupted:
        status = 'interrupted'
    report = {
        'schema_version': 1, 'status': status,
        'command': command, 'cwd': str(cwd), 'started_at': started, 'finished_at': utc_now(),
        'elapsed_seconds': round(time.monotonic() - before, 4), 'timeout_seconds': timeout,
        'returncode': returncode, 'timed_out': timed_out, 'interrupted': interrupted,
        'launch_error': launch_error, 'required_markers': markers, 'missing_markers': missing,
        'error_count': error_count, 'error_lines': error_lines,
        'error_detection': 'common-line-prefix-heuristic; not a complete test protocol parser',
        'completion_marker_checked': bool(markers), 'proves_game_quality': False,
        'process_cleanup': 'POSIX process group' if os.name == 'posix' else 'direct child only',
        'logs': {label: {'path': path.name, 'bytes': path.stat().st_size, 'sha256': digest(path)}
                 for label, path in [('stdout', stdout_path), ('stderr', stderr_path)]},
    }
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    code = 0 if passed else (124 if timed_out else (130 if interrupted else (2 if launch_error else 1)))
    return report, code


def main(argv: list[str] | None = None) -> int:
    """Parse the wrapper CLI and refuse ambiguous or stale evidence paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='NEW evidence directory; never overwrites')
    parser.add_argument('--cwd', type=Path, default=Path.cwd(), help='Existing command working directory')
    parser.add_argument('--timeout', type=float, default=120.0, help='Positive finite seconds')
    parser.add_argument('--require-text', action='append', default=[], help='Literal completion marker; repeatable')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Explicit command after -- (no shell)')
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('an explicit command after -- is required')
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error('--timeout must be a positive finite number')
    if any(not text or len(text.encode('utf-8')) > 4096 for text in args.require_text):
        parser.error('--require-text must contain 1..4096 UTF-8 bytes')
    cwd = args.cwd.expanduser().resolve()
    if not cwd.is_dir():
        parser.error('--cwd must be an existing directory')
    out = args.out.expanduser().absolute()
    if out.exists() or out.is_symlink():
        parser.error('--out must not already exist (fresh evidence only)')
    try:
        report, code = execute(command, cwd, args.timeout, out, args.require_text)
    except OSError as exc:
        print(f'evidence write failed: {exc}', file=sys.stderr)
        return 2
    print(json.dumps({'status': report['status'], 'report': str(out / 'report.json')}, ensure_ascii=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())

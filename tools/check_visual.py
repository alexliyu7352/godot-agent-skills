#!/usr/bin/env python3
"""Capture a rendered Godot fixture; never infer a visual review from exit zero.

Run inside an existing X server, for example xvfb-run. No engine or fonts are
installed by this script. A fresh directory and explicit engine are mandatory.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SIZES = [(800, 600), (1280, 720), (1600, 900)]
FAULTS = {
    'text-clipping': ('body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART',
                      'body.autowrap_mode = TextServer.AUTOWRAP_OFF\n\tbody.clip_text = true', 'text/wrapped'),
    'pointer-blocker': ('blocker.mouse_filter = Control.MOUSE_FILTER_IGNORE',
                        'blocker.mouse_filter = Control.MOUSE_FILTER_STOP', 'input/click-delivered'),
}


def prepare_visual(out: Path, variant: str = 'baseline') -> None:
    """Copy only the render fixture and two used helpers to a disposable project."""
    if out.exists() or out.is_symlink():
        raise ValueError('visual destination must not exist')
    if variant not in ('baseline', *FAULTS):
        raise ValueError('unknown visual variant')
    shutil.copytree(ROOT / 'evals/visual', out)
    (out / 'examples').mkdir()
    for filename, skill in [('choice_routes.gd', 'godot-dialogue'), ('local_theme.gd', 'godot-ui')]:
        shutil.copyfile(ROOT / 'skills' / skill / 'references' / filename, out / 'examples' / filename)
    if variant != 'baseline':
        path = out / 'ui_fixture.gd'
        text = path.read_text(encoding='utf-8')
        old, new, _ = FAULTS[variant]
        if text.count(old) != 1:
            raise ValueError('visual mutation needs review: ' + variant)
        path.write_text(text.replace(old, new), encoding='utf-8')


def engine_command(godot: str, project: Path, width: int, height: int) -> list[str]:
    """Request an actual X11 window/OpenGL render target, never headless fallback."""
    return [godot, '--path', str(project), '--display-driver', 'x11',
            '--rendering-method', 'gl_compatibility', '--audio-driver', 'Dummy',
            '--resolution', f'{width}x{height}', '--script', 'res://capture.gd']


def matches_expected(code: int, stdout: str, stderr: str, capture: dict, variant: str) -> bool:
    """Require completed capture and target assertions; parser failure is not a win."""
    if not capture.get('capture_complete') or 'VISUAL_DONE' not in stdout:
        return False
    if variant == 'baseline':
        return code == 0 and capture.get('failures') == []
    return code != 0 and ('ASSERT FAIL: ' + FAULTS[variant][2]) in stderr


def image_record(path: Path, width: int, height: int) -> dict:
    """Validate PNG dimensions and hash the actual bytes without evaluating beauty."""
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise ValueError('not a PNG: ' + str(path))
    if struct.unpack('>II', data[16:24]) != (width, height):
        raise ValueError('unexpected capture dimensions: ' + str(path))
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'width': width, 'height': height}


def run_visual(godot: str, out: Path) -> dict:
    """Run three good viewport sizes and two isolated known bad UI variants."""
    version = subprocess.run([godot, '--version'], capture_output=True, text=True, timeout=15, check=True)
    wrapper = ROOT / 'skills/godot-verification/scripts/run_check.py'
    outcomes = []
    jobs = [('baseline', w, h) for w, h in SIZES] + [(fault, 800, 600) for fault in FAULTS]
    for variant, width, height in jobs:
        name = f'{variant}-{width}x{height}'
        project, evidence = out / 'work' / name, out / 'logs' / name
        prepare_visual(project, variant)
        # Code-only fixtures need no asset imports. All preloads use explicit paths.
        command = [sys.executable, str(wrapper), '--cwd', str(project), '--out', str(evidence),
                   '--timeout', '50', '--require-text', 'VISUAL_DONE', '--']
        result = subprocess.run(command + engine_command(godot, project, width, height),
                                capture_output=True, text=True, timeout=65)
        stdout = (evidence / 'stdout.log').read_text(encoding='utf-8', errors='replace') if evidence.exists() else ''
        stderr = (evidence / 'stderr.log').read_text(encoding='utf-8', errors='replace') if evidence.exists() else result.stderr
        capture_path = project / 'capture.json'
        capture = json.loads(capture_path.read_text(encoding='utf-8')) if capture_path.exists() else {}
        passed = matches_expected(result.returncode, stdout, stderr, capture, variant)
        images = []
        if capture.get('display') == 'headless' or capture.get('renderer') != 'gl_compatibility':
            passed = False
        for state in ['long-text', 'no-choices', 'returned']:
            source = project / 'captures' / (state + '.png')
            try:
                info = image_record(source, width, height)
                target = out / 'images' / name / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                images.append({'state': state, 'file': str(target.relative_to(out)), **info})
            except (OSError, ValueError) as exc:
                stderr += '\n' + str(exc)
                passed = False
        outcomes.append({'name': name, 'variant': variant, 'passed': passed,
                         'expected_failure': variant != 'baseline', 'capture': capture,
                         'images': images, 'evidence': str(evidence.relative_to(out))})
        print(f'{name}: {"PASS" if passed else "FAIL"}', flush=True)
        if not passed:
            print((stdout + stderr)[-6000:], flush=True)
    summary = {'schema_version': 1, 'engine': version.stdout.strip(),
               'status': 'passed' if all(x['passed'] for x in outcomes) else 'failed',
               'runs': outcomes, 'visual_pixels_reviewed': False, 'agent_behavior_tested': False,
               'scope': 'synthetic fixture pixels, layout and Viewport input, not user game or OS input'}
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return summary


def main(argv: list[str] | None = None) -> int:
    """Use the caller's display/engine and preserve all outputs in a new directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        executable = shutil.which(args.godot)
        if not executable:
            raise ValueError('Godot executable not found')
        out = args.out.expanduser().absolute()
        out.mkdir(parents=True, exist_ok=False)
        return 0 if run_visual(executable, out)['status'] == 'passed' else 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'VISUAL CHECK FAILED: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

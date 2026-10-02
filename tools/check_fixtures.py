#!/usr/bin/env python3
"""Prepare/run small Godot contracts and faulted variants, not coding-agent evals.

No download, model selection or access to a user's game. --out must be new.
--prepare-only exports one ready-to-run fixture for an independently configured
coding agent; run mode invokes only the explicitly supplied Godot executable.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    'scene_snapshot.gd': 'godot-code-scenes',
    'runtime_state.gd': 'godot-data-state',
    'local_theme.gd': 'godot-ui',
    'choice_routes.gd': 'godot-dialogue',
    'save_envelope.gd': 'godot-save-load',
}
# Faults are applied only to disposable copies, never to shipped helper behavior.
MUTATIONS = {
    'scene-owner': ('scene_snapshot.gd', '\tvar error := packed.pack(root)',
                    '\troot.get_node("Button").owner = null\n\tvar error := packed.pack(root)', 'build', 'scene/button retained'),
    'resource-alias': ('runtime_state.gd', 'counters.duplicate(true)', 'counters', 'logic', 'resource/nested state isolated'),
    'ui-shared-theme': ('local_theme.gd', 'original.duplicate() as StyleBoxFlat', 'original', 'logic', 'ui/shared theme unchanged'),
    'dialogue-empty': ('choice_routes.gd', 'routes.append({"id": "__return__", "kind": "return"})',
                       'pass', 'logic', 'dialogue/zero choices has route'),
    'future-save': ('save_envelope.gd', 'if version > current_version:', 'if false:', 'reload', 'save/future refused'),
}


def prepare(destination: Path, variant: str = 'baseline') -> None:
    """Export a fresh fixture with exactly the reviewed examples and optional fault."""
    if destination.exists() or destination.is_symlink():
        raise ValueError('fixture destination must not exist')
    shutil.copytree(ROOT / 'evals/fixtures', destination)
    examples = destination / 'examples'
    examples.mkdir()
    for filename, skill in EXAMPLES.items():
        shutil.copyfile(ROOT / 'skills' / skill / 'references' / filename, examples / filename)
    if variant != 'baseline':
        filename, old, new, _, _ = MUTATIONS[variant]
        path = examples / filename
        text = path.read_text(encoding='utf-8')
        if text.count(old) != 1:
            raise ValueError(f'mutation anchor changed: {variant}; review the fault, do not silently skip it')
        path.write_text(text.replace(old, new), encoding='utf-8')


def invoke(godot: str, work: Path, evidence: Path, mode: str) -> dict:
    """Use stable command capture and retain logs for each actual engine process."""
    wrapper = ROOT / 'skills/godot-verification/scripts/run_check.py'
    command = [sys.executable, str(wrapper), '--out', str(evidence), '--cwd', str(work), '--timeout', '45']
    engine = [godot, '--headless', '--path', str(work)]
    if mode == 'import':
        engine += ['--editor', '--import']
    else:
        command += ['--require-text', 'FIXTURE_DONE']
        engine += ['--script', 'res://checks.gd', '--', mode]
    result = subprocess.run(command + ['--'] + engine, capture_output=True, text=True, timeout=60)
    path = evidence / 'report.json'
    report = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    stdout = (evidence / 'stdout.log').read_text(encoding='utf-8', errors='replace') if path.exists() else ''
    stderr = (evidence / 'stderr.log').read_text(encoding='utf-8', errors='replace') if path.exists() else result.stderr
    return {'returncode': result.returncode, 'report': report, 'stdout': stdout, 'stderr': stderr}


def run(godot: str, out: Path) -> dict:
    """Run the good implementation and require every injected bug to fail correctly."""
    version = subprocess.run([godot, '--version'], capture_output=True, text=True, timeout=15)
    if version.returncode:
        raise ValueError('Godot --version failed: ' + version.stderr)
    outcomes = []
    for variant in ['baseline', *MUTATIONS]:
        work = out / 'work' / variant
        prepare(work, variant)
        modes = ['import', 'build', 'reload', 'logic'] if variant == 'baseline' else ['import']
        if variant != 'baseline':
            mode = MUTATIONS[variant][3]
            modes += ['build', 'reload'] if mode == 'reload' else [mode]
        for mode in modes:
            evidence = out / 'logs' / variant / mode
            result = invoke(godot, work, evidence, mode)
            expected_failure = variant != 'baseline' and mode == MUTATIONS[variant][3]
            if expected_failure:
                marker = 'ASSERT FAIL: ' + MUTATIONS[variant][4]
                passed = result['returncode'] != 0 and marker in result['stderr'] and 'FIXTURE_DONE' in result['stdout']
            else:
                passed = result['returncode'] == 0 and result['report'].get('status') == 'command_passed'
            outcomes.append({'variant': variant, 'mode': mode, 'passed': passed,
                             'expected_failure': expected_failure, 'evidence': str(evidence.relative_to(out))})
            print(f'{variant}/{mode}: {"PASS" if passed else "FAIL"}', flush=True)
            if not passed:
                print(result['stdout'][-5000:] + result['stderr'][-5000:], flush=True)
                break
    summary = {'engine': version.stdout.strip(), 'status': 'passed' if all(x['passed'] for x in outcomes) else 'failed',
               'checks': outcomes, 'agent_behavior_tested': False, 'visual_pixels_reviewed': False,
               'scope': 'headless Godot helper contracts, synthetic GUI events, fault detection; no game-quality proof'}
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return summary


def main(argv=None) -> int:
    """Provide a no-network preparation/run command with explicit fresh outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', help='Explicit executable for run mode')
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--variant', choices=['baseline', *MUTATIONS], default='baseline')
    args = parser.parse_args(argv)
    out = args.out.expanduser().absolute()
    try:
        if args.prepare_only:
            prepare(out, args.variant)
            print(f'Prepared {args.variant}: {out}; engine/agent tests NOT_RUN')
            return 0
        if not args.godot:
            parser.error('--godot is required unless --prepare-only is used')
        out.mkdir(parents=True, exist_ok=False)
        godot = shutil.which(args.godot)
        if not godot:
            raise ValueError('Godot executable not found: ' + args.godot)
        return 0 if run(godot, out)['status'] == 'passed' else 1
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f'FIXTURE CHECK FAILED: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

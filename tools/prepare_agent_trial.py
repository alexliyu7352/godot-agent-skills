#!/usr/bin/env python3
"""Prepare an isolated task-only Godot trial, or grade a completed project copy.

This is not a model runner. It neither selects a model nor performs authentication
or network calls. Directory separation is not an access-control boundary: the
operator must restrict the real agent to the project directory for a fair trial.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_fixtures

TASKS = {
    'scene-owner': 'Godot 程序保存场景后交谈按钮消失。修复后，磁盘重载应保留按钮、导出引用和原有信号连接。只修改必要实现。',
    'resource-alias': '两名 Godot 人物的独立计数互相污染。修复嵌套计数和列表的共享问题，同时保留允许共享的外观定义。',
    'ui-shared-theme': 'Godot 一个 PanelContainer 的边框改为 4 像素时，共用 Theme 的另一面板也被改变。请只修复局部样式，不改变其他面板。',
    'dialogue-empty': 'Godot NPC 的两个选项条件都不满足时，玩家没有可选项，也无法离开。修复为可以明确返回，并保留点击时重新验证条件的行为。',
    'future-save': '当前 Godot 程序只支持版本 2 的存档，却接受版本 5 并改变当前状态。请明确拒绝未来版本，保留原文件和旧状态，不伪造迁移。',
}
IGNORED = {'.git', '.godot', '.agents', '.claude'}


def sha(path: Path) -> str:
    """Fingerprint file bytes for reproducible trial provenance."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_fingerprint(project: Path) -> str:
    """Compare task source content while excluding only caches and host skills."""
    digest = hashlib.sha256()
    for path in sorted(project.rglob('*')):
        relative = path.relative_to(project)
        if any(part in IGNORED for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError('trial source may not contain symlinks: ' + str(relative))
        if path.is_file():
            digest.update(str(relative).encode('utf-8') + b'\0' + sha(path).encode('ascii') + b'\n')
    return digest.hexdigest()


def prepare_trial(out: Path, variant: str, host: str, with_skills: bool) -> dict:
    """Export identical faulty task content; treatment adds only the reviewed pack."""
    if variant not in TASKS or host not in ('codex', 'claude'):
        raise ValueError('unknown variant or host')
    if out.exists() or out.is_symlink():
        raise ValueError('trial output must be new')
    out.mkdir(parents=True)
    project = out / 'project'
    check_fixtures.prepare(project, variant)
    grader = out / 'grader'
    grader.mkdir()
    for name in ['checks.gd', 'README.md']:
        shutil.move(str(project / name), str(grader / name))
    (project / '.gitignore').write_text('.godot/\n', encoding='utf-8')
    (out / 'task.txt').write_text(TASKS[variant] + '\n', encoding='utf-8')
    fingerprint = project_fingerprint(project)
    if with_skills:
        result = subprocess.run([sys.executable, str(ROOT / 'tools/install.py'), '--host', host,
                                 '--project', str(project)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise ValueError('trial skill installation failed: ' + result.stdout + result.stderr)
        (out / 'installation.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
    subprocess.run(['git', 'init', '--quiet', str(project)], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(project), 'add', '.'], check=True, capture_output=True)
    subprocess.run(['git', '-C', str(project), '-c', 'user.name=Skill Eval Fixture',
                    '-c', 'user.email=fixture@localhost', 'commit', '--quiet', '-m', 'Starting task fixture'],
                   check=True, capture_output=True)
    starting_commit = subprocess.run(['git', '-C', str(project), 'rev-parse', 'HEAD'],
                                    capture_output=True, text=True, check=True).stdout.strip()
    record = {'schema_version': 1, 'status': 'NOT_RUN', 'variant': variant, 'host': host,
              'condition': 'with_skills' if with_skills else 'without_skills',
              'project_sha256': fingerprint, 'task_sha256': sha(out / 'task.txt'),
              'pack_sha256': sha(ROOT / 'pack.json'), 'grader_sha256': sha(grader / 'checks.gd'),
              'starting_commit': starting_commit, 'model': None, 'reasoning': None,
              'agent_trace': None, 'selection_result': None, 'task_result': None,
              'limitation': 'The sibling grader is NOT hidden by filesystem permissions. Restrict the host scope.'}
    (out / 'trial.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return record


def grade_trial(trial: Path, godot: str, out: Path) -> dict:
    """Grade a disposable candidate copy with this checkout's untouched assertions."""
    record = json.loads((trial / 'trial.json').read_text(encoding='utf-8'))
    if record.get('pack_sha256') != sha(ROOT / 'pack.json'):
        raise ValueError('grader/pack version mismatch; use the preparing checkout')
    trusted = ROOT / 'evals/fixtures/checks.gd'
    if record.get('grader_sha256') != sha(trusted):
        raise ValueError('trusted grader changed; do not mix trial versions')
    candidate = trial / 'project'
    candidate_hash = project_fingerprint(candidate)
    out.mkdir(parents=True, exist_ok=False)
    work = out / 'project'
    shutil.copytree(candidate, work, ignore=shutil.ignore_patterns(*IGNORED, 'checks.gd'))
    shutil.copyfile(trusted, work / 'checks.gd')
    outcomes = []
    for mode in ['import', 'build', 'reload', 'logic']:
        result = check_fixtures.invoke(godot, work, out / 'logs' / mode, mode)
        passed = result['returncode'] == 0 and result['report'].get('status') == 'command_passed'
        outcomes.append({'mode': mode, 'passed': passed})
        print(f'{mode}: {"PASS" if passed else "FAIL"}', flush=True)
        if not passed:
            print((result['stdout'] + result['stderr'])[-5000:], flush=True)
            break
    summary = {'schema_version': 1, 'status': 'task_contract_passed' if all(x['passed'] for x in outcomes) else 'task_contract_failed',
               'candidate_sha256': candidate_hash, 'checks': outcomes,
               'agent_behavior_tested': False, 'selection_result': None,
               'scope': 'fixed helper contracts only; requires separate real-host trace and diff review'}
    (out / 'result.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return summary


def main(argv: list[str] | None = None) -> int:
    """Expose preparation/grading without launching or impersonating a coding agent."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    prepare = commands.add_parser('prepare')
    prepare.add_argument('--variant', required=True, choices=sorted(TASKS))
    prepare.add_argument('--host', required=True, choices=['codex', 'claude'])
    prepare.add_argument('--with-skills', action='store_true')
    prepare.add_argument('--out', required=True, type=Path)
    grade = commands.add_parser('grade')
    grade.add_argument('--trial', required=True, type=Path)
    grade.add_argument('--godot', required=True)
    grade.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        out = args.out.expanduser().absolute()
        if args.action == 'prepare':
            result = prepare_trial(out, args.variant, args.host, args.with_skills)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        executable = shutil.which(args.godot)
        if not executable:
            raise ValueError('Godot executable not found')
        result = grade_trial(args.trial.expanduser().resolve(), executable, out)
        return 0 if result['status'] == 'task_contract_passed' else 1
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f'TRIAL FAILED: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

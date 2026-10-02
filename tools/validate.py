#!/usr/bin/env python3
"""Validate packaging, local references, metadata and test-case definitions.

This does not run an agent, Godot or a graphics backend; no behavior/quality claim
may be inferred from this static report.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys

from packlib import SKILLS, load_manifest, read_json, safe_relative

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
PROHIBITED = re.compile(r'(?im)^(?:model|context|hooks|allowed-tools|agent):|^\s*!`')


def frontmatter(text: str) -> dict[str, str]:
    """Parse this pack's intentionally small scalar-only YAML subset."""
    parts = text.split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError('missing YAML frontmatter')
    values = {}
    for line in parts[1].strip().splitlines():
        key, separator, raw = line.partition(':')
        if not separator or key not in {'name', 'description', 'license'} or key in values:
            raise ValueError('unexpected/duplicate frontmatter field: ' + key)
        raw = raw.strip()
        value = json.loads(raw) if raw.startswith('"') else raw
        if not isinstance(value, str) or not value:
            raise ValueError('frontmatter values must be non-empty scalar strings')
        values[key] = value
    if set(values) != {'name', 'description', 'license'}:
        raise ValueError('name, description and license are required by this pack')
    return values


def check_links(path: Path, boundary: Path) -> None:
    """Require each local Markdown link to stay inside its installed skill."""
    text = path.read_text(encoding='utf-8')
    for link in LINK.findall(text):
        if link.startswith(('https://', 'http://', 'mailto:', '#')):
            continue
        relative = link.split('#', 1)[0]
        if not relative:
            continue
        safe_relative(relative)
        target = (path.parent / relative).resolve()
        if not target.is_relative_to(boundary.resolve()) or not target.is_file():
            raise ValueError(f'broken/out-of-skill reference: {path}: {link}')


def check_docstrings(path: Path) -> None:
    """Verify every authored named Python class and function has a docstring."""
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not ast.get_docstring(node):
            raise ValueError(f'missing docstring: {path}:{node.lineno} {node.name}')


def check_cases(path: Path) -> int:
    """Check evaluation definitions, without pretending to execute their prompts."""
    ids = set()
    positive_coverage = set()
    negative_count = 0
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        case = json.loads(line)
        if not isinstance(case['prompt'], str) or not case['prompt'] or case['id'] in ids:
            raise ValueError(f'invalid case or duplicate ID on line {number}')
        ids.add(case['id'])
        allowed = set(case['allowed_pack_skills'])
        primary = set(case['expected_primary_any'])
        if not primary <= allowed <= SKILLS:
            raise ValueError(f'unknown/contradictory skill sets in {case["id"]}')
        if not isinstance(case['checks'], list) or not case['checks']:
            raise ValueError(f'missing behavioral rubric in {case["id"]}')
        if case['kind'] == 'negative':
            negative_count += 1
            if primary:
                raise ValueError('negative case cannot require a pack skill')
        else:
            positive_coverage |= primary
    if positive_coverage != SKILLS or negative_count < 4:
        raise ValueError('evaluation cases must cover all seven skills and at least four negatives')
    return len(ids)


def validate(root: Path) -> dict:
    """Validate exactly the promised install surface and reproducibility metadata."""
    manifest = load_manifest(root)
    discovered = list((root / 'skills').rglob('SKILL.md'))
    if len(discovered) != 7 or {path.parent.name for path in discovered} != SKILLS:
        raise ValueError('unexpected discoverable skill entry')
    stats = []
    for path in sorted(discovered):
        text = path.read_text(encoding='utf-8')
        meta = frontmatter(text)
        if meta['name'] != path.parent.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', meta['name']):
            raise ValueError(f'invalid skill name: {path}')
        if len(meta['name']) > 64 or not 1 <= len(meta['description']) <= 500:
            raise ValueError('metadata exceeds this pack\'s budget')
        if meta['license'] != 'Apache-2.0':
            raise ValueError('unexpected license declaration')
        if len(text.encode('utf-8')) > 9000 or len(text.splitlines()) > 120:
            raise ValueError('entry too large; move task-specific detail to references')
        for document in path.parent.rglob('*.md'):
            if PROHIBITED.search(document.read_text(encoding='utf-8')):
                raise ValueError(f'unexpected host/model/dynamic configuration: {document}')
            check_links(document, path.parent)
        if (path.parent / 'LICENSE.txt').stat().st_size < 11000:
            raise ValueError('missing complete bundled license notices')
        stats.append({'name': meta['name'], 'entry_bytes': len(text.encode('utf-8')),
                      'entry_lines': len(text.splitlines()), 'description_characters': len(meta['description'])})
    sources = read_json(root / 'sources.lock.json')
    if len(sources['upstreams']) != 3 or set(sources['skills']) != SKILLS:
        raise ValueError('incomplete source provenance')
    for upstream in sources['upstreams']:
        if not re.fullmatch(r'[0-9a-f]{40}', upstream['commit']):
            raise ValueError('source not pinned to a full commit')
    for path in root.rglob('*.py'):
        if '.git' not in path.parts:
            check_docstrings(path)
    cases = check_cases(root / 'evals/cases.jsonl')
    return {'status': 'static_validation_passed', 'version': manifest['version'],
            'skills': stats, 'runtime_files': sum(len(item['files']) for item in manifest['skills'].values()),
            'evaluation_cases_defined': cases, 'agent_behavior_tested': False, 'godot_engine_tested': False}


def main(argv: list[str] | None = None) -> int:
    """Expose a deterministic, offline package-validation command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--json', type=Path, help='Write report to a new file (no overwrite)')
    args = parser.parse_args(argv)
    try:
        result = validate(args.root.resolve())
        text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        if args.json:
            with args.json.open('x', encoding='utf-8') as stream:
                stream.write(text)
        print(text, end='')
        return 0
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as exc:
        print(f'VALIDATION FAILED: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

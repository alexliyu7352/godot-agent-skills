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


def nonempty_text(value, label: str) -> str:
    """Reject non-string and blank schema values with a useful field label."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be a nonblank string')
    return value


def text_list(value, label: str, *, nonempty: bool = True) -> list[str]:
    """Validate list element types without accepting a string as an iterable."""
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(f'{label} must be a list of nonblank strings')
    for item in value:
        nonempty_text(item, label)
    if len(value) != len(set(value)):
        raise ValueError(f'{label} contains duplicate values')
    return value


def check_cases(path: Path) -> int:
    """Validate positive/negative contracts; this does not execute any prompt."""
    ids = set()
    positive_coverage = set()
    negative_count = 0
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        case = json.loads(line)
        if not isinstance(case, dict):
            raise ValueError(f'case on line {number} must be an object')
        case_id = nonempty_text(case.get('id'), 'case ID')
        nonempty_text(case.get('prompt'), 'prompt')
        if case_id in ids:
            raise ValueError(f'duplicate case ID: {case_id}')
        ids.add(case_id)
        if case.get('kind') not in ('positive', 'negative'):
            raise ValueError(f'unknown case kind: {case_id}')
        allowed = set(text_list(case.get('allowed_pack_skills'), 'allowed skills', nonempty=False))
        primary = set(text_list(case.get('expected_primary_any'), 'primary skills', nonempty=False))
        if not primary <= allowed <= SKILLS:
            raise ValueError(f'unknown/contradictory skill sets in {case_id}')
        text_list(case.get('checks'), 'checks')
        if case['kind'] == 'negative':
            negative_count += 1
            if primary or allowed:
                raise ValueError('negative case must forbid all pack skills')
        else:
            if not primary:
                raise ValueError(f'positive case needs a primary candidate: {case_id}')
            positive_coverage |= primary
    if positive_coverage != SKILLS or negative_count < 4:
        raise ValueError('cases must cover all seven skills and at least four negatives')
    return len(ids)


def check_sources(sources: dict) -> None:
    """Check pinned provenance references offline; do not claim remote existence."""
    if not isinstance(sources, dict) or sources.get('schema_version') != 1:
        raise ValueError('unsupported provenance schema')
    upstreams = sources.get('upstreams')
    if not isinstance(upstreams, list) or len(upstreams) != 3:
        raise ValueError('expected three declared upstreams')
    index = {}
    for upstream in upstreams:
        if not isinstance(upstream, dict):
            raise ValueError('upstream must be an object')
        key = nonempty_text(upstream.get('id'), 'upstream ID')
        if key in index:
            raise ValueError(f'duplicate upstream ID: {key}')
        repository = nonempty_text(upstream.get('repository'), 'repository')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('repository must be owner/name')
        commit = nonempty_text(upstream.get('commit'), 'commit')
        if not re.fullmatch(r'[0-9a-f]{40}', commit):
            raise ValueError('source not pinned to a full commit')
        nonempty_text(upstream.get('license'), 'license')
        safe_relative(nonempty_text(upstream.get('license_path'), 'license path'))
        if 'notice_path' in upstream:
            safe_relative(nonempty_text(upstream['notice_path'], 'notice path'))
        index[key] = upstream
    mappings = sources.get('skills')
    if not isinstance(mappings, dict) or set(mappings) != SKILLS:
        raise ValueError('incomplete skill provenance')
    for skill, mapping in mappings.items():
        if not isinstance(mapping, dict):
            raise ValueError(f'invalid source mapping: {skill}')
        nonempty_text(mapping.get('decision'), 'curation decision')
        inputs = mapping.get('inputs')
        if not isinstance(inputs, list) or not inputs:
            raise ValueError(f'missing source inputs: {skill}')
        seen = set()
        for item in inputs:
            if not isinstance(item, dict):
                raise ValueError('source input must be an object')
            key = nonempty_text(item.get('upstream'), 'input upstream')
            if key not in index:
                raise ValueError(f'unknown upstream: {key}')
            path = nonempty_text(item.get('path'), 'source path')
            safe_relative(path)
            upstream = index[key]
            url = f"https://github.com/{upstream['repository']}/blob/{upstream['commit']}/{path}"
            if item.get('url') != url or (key, path) in seen:
                raise ValueError(f'inconsistent or duplicate source URL: {skill}: {path}')
            seen.add((key, path))


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
    check_sources(sources)
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

"""Small standard-library helpers shared by validation and project installation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re

PACK_ID = 'godot-agent-skills'
SKILLS = frozenset({
    'godot-code-scenes', 'godot-data-state', 'godot-ui', 'godot-dialogue',
    'godot-save-load', 'godot-debugging', 'godot-verification',
})
SHA256 = re.compile(r'^[0-9a-f]{64}$')


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    """Reject duplicate JSON keys rather than silently changing an allowlist."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    """Read strict UTF-8 JSON metadata with duplicate-key rejection."""
    value = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
    if not isinstance(value, dict):
        raise ValueError(f'expected JSON object: {path}')
    return value


def safe_relative(value: str) -> PurePosixPath:
    """Validate a literal portable path without normalizing away traversal."""
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError(f'invalid relative path: {value!r}')
    parts = value.split('/')
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ('', '.', '..') for part in parts):
        raise ValueError(f'unsafe relative path: {value!r}')
    return path


def reject_symlinks(path: Path) -> None:
    """Refuse links in any existing component before filesystem mutations."""
    absolute = path.absolute()
    for candidate in [*reversed(absolute.parents), absolute]:
        if candidate.is_symlink():
            raise ValueError(f'symlink not supported: {candidate}')


def file_hash(path: Path) -> str:
    """Hash one regular file in bounded memory."""
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            value.update(block)
    return value.hexdigest()


def scan_regular_files(root: Path) -> dict[str, str]:
    """Inventory regular files and reject links or special files in a skill root."""
    reject_symlinks(root)
    if not root.is_dir():
        raise ValueError(f'missing directory: {root}')
    files = {}
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError(f'symlink not supported: {path}')
        if path.is_file():
            files[path.relative_to(root).as_posix()] = file_hash(path)
        elif not path.is_dir():
            raise ValueError(f'non-regular entry: {path}')
    return files


def load_manifest(root: Path) -> dict:
    """Load a seven-skill allowlist and verify every installable source byte."""
    reject_symlinks(root)
    manifest = read_json(root / 'pack.json')
    if manifest.get('schema_version') != 1 or manifest.get('id') != PACK_ID:
        raise ValueError('unsupported pack manifest')
    if not isinstance(manifest.get('version'), str) or not manifest['version']:
        raise ValueError('missing pack version')
    skills = manifest.get('skills')
    if not isinstance(skills, dict) or set(skills) != SKILLS:
        raise ValueError('manifest must contain exactly the seven approved skills')
    expected_all = {}
    for name, item in skills.items():
        files = item.get('files') if isinstance(item, dict) else None
        if not isinstance(files, dict) or not {'SKILL.md', 'LICENSE.txt'} <= set(files):
            raise ValueError(f'missing skill entry/license: {name}')
        for relative, expected_hash in files.items():
            safe_relative(relative)
            if not isinstance(expected_hash, str) or not SHA256.fullmatch(expected_hash):
                raise ValueError(f'invalid source hash: {name}/{relative}')
            expected_all[f'{name}/{relative}'] = expected_hash
    actual_all = scan_regular_files(root / 'skills')
    if actual_all != expected_all:
        changed = sorted(set(actual_all) ^ set(expected_all) |
                         {path for path in actual_all.keys() & expected_all.keys()
                          if actual_all[path] != expected_all[path]})
        raise ValueError('source differs from reviewed allowlist: ' + ', '.join(changed[:12]))
    return manifest


def installed_hashes(manifest: dict) -> dict[str, str]:
    """Flatten install paths relative to the host's skills directory."""
    return {f'{name}/{path}': value for name, item in manifest['skills'].items()
            for path, value in item['files'].items()}

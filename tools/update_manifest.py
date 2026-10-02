#!/usr/bin/env python3
"""Rehash already-allowlisted files; never silently add new runtime content."""
from __future__ import annotations

import json
from pathlib import Path

from packlib import SKILLS, file_hash, read_json, reject_symlinks, safe_relative

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Refresh explicit reviewed entries and keep newly added files unlisted."""
    target = ROOT / 'pack.json'
    manifest = read_json(target)
    if set(manifest['skills']) != SKILLS:
        raise ValueError('the seven-skill boundary changed; explicit design review required')
    for name, item in manifest['skills'].items():
        for relative in item['files']:
            safe_relative(relative)
            path = ROOT / 'skills' / name / relative
            reject_symlinks(path)
            if not path.is_file():
                raise ValueError(f'allowlisted file missing: {path}')
            item['files'][relative] = file_hash(path)
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    target.write_text(text, encoding='utf-8')
    print('Updated existing allowlist hashes; run tools/validate.py and tests before publishing.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

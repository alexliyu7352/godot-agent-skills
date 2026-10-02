#!/usr/bin/env python3
"""Install only this pack into an existing project, preserving unrelated files.

No global install, model changes, network, hooks or forced overwrite. Managed
updates/removal require unchanged recorded files. The receipt is an ownership
record, not a signature or a defense against a hostile concurrent filesystem.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from packlib import (PACK_ID, SKILLS, SHA256, installed_hashes, load_manifest,
                     read_json, reject_symlinks, safe_relative, scan_regular_files)

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = '.godot-agent-skills.receipt.json'
LOCK = '.godot-agent-skills.lock'


class RollbackIncomplete(RuntimeError):
    """Signal that recovery material and the cooperative lock must be retained."""


class MutationRolledBack(RuntimeError):
    """Report a failed mutation whose installed state was restored."""

    def __init__(self, original: BaseException, cleanup_path: Path | None = None):
        """Retain the original failure and any leftover disposable staging directory."""
        super().__init__(str(original))
        self.cleanup_path = cleanup_path


def read_receipt(path: Path, host: str) -> dict | None:
    """Validate receipt ownership paths before they can authorize any removal."""
    reject_symlinks(path)
    if not path.exists():
        return None
    data = read_json(path)
    if data.get('schema_version') != 1 or data.get('id') != PACK_ID or data.get('host') != host:
        raise ValueError('unrecognized install receipt; refusing overwrite')
    files = data.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('invalid receipt files')
    for name, value in files.items():
        relative = safe_relative(name)
        if len(relative.parts) < 2 or relative.parts[0] not in SKILLS:
            raise ValueError(f'receipt path outside approved skills: {name}')
        if not isinstance(value, str) or not SHA256.fullmatch(value):
            raise ValueError(f'invalid receipt hash: {name}')
    if {path.split('/')[0] for path in files} != SKILLS:
        raise ValueError('receipt does not own exactly the approved skills')
    return data


def preflight(destination: Path, host: str, manifest: dict, update: bool, remove: bool) -> tuple[str, dict | None]:
    """Check every collision before touching any installed skill or receipt."""
    reject_symlinks(destination)
    old = read_receipt(destination / RECEIPT, host)
    if old is None:
        if remove:
            raise ValueError('no managed installation receipt; nothing will be removed')
        for name in SKILLS:
            path = destination / name
            if path.exists() or path.is_symlink():
                raise ValueError(f'unmanaged skill collision: {path}; preserve/review it manually')
        return 'install', None
    observed = {}
    for name in SKILLS:
        folder = destination / name
        observed.update({f'{name}/{path}': value for path, value in scan_regular_files(folder).items()})
    if observed != old['files']:
        raise ValueError('installed files were edited, added or removed; refusing update/removal')
    if remove:
        return 'uninstall', old
    if old['files'] == installed_hashes(manifest) and old.get('version') == manifest['version']:
        return 'unchanged', old
    if not update:
        raise ValueError('a different managed pack is installed; review changes then use --update')
    return 'update', old


def mutate(destination: Path, action: str, manifest: dict, host: str) -> dict:
    """Stage all files then replace owned directories, rolling back normal failures.

    Process/power loss is not transactionally recovered; the lock is deliberately
    retained by abrupt termination. A caller must inspect any surviving staging
    directory before manually removing a stale lock.
    """
    receipt_path = destination / RECEIPT
    original_receipt = receipt_path.read_bytes() if receipt_path.exists() else None
    staging = Path(tempfile.mkdtemp(prefix='.godot-agent-skills-stage-', dir=destination.parent))
    new_root, old_root = staging / 'new', staging / 'old'
    new_root.mkdir()
    old_root.mkdir()
    moved_old: list[str] = []
    placed_new: list[str] = []
    receipt_touched = False
    try:
        if action != 'uninstall':
            for name, item in manifest['skills'].items():
                for relative in item['files']:
                    source = ROOT / 'skills' / name / relative
                    target = new_root / name / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, target)
            # Recheck staged bytes to catch a source change during copying.
            if scan_regular_files(new_root) != installed_hashes(manifest):
                raise ValueError('staged files changed during copy; installation stopped')
        destination.mkdir(parents=True, exist_ok=True)
        for name in sorted(SKILLS):
            target = destination / name
            if target.exists():
                os.replace(target, old_root / name)
                moved_old.append(name)
            if action != 'uninstall':
                os.replace(new_root / name, target)
                placed_new.append(name)
        receipt_touched = True
        if action == 'uninstall':
            receipt_path.unlink()
        else:
            receipt = {'schema_version': 1, 'id': PACK_ID, 'version': manifest['version'],
                       'host': host, 'files': installed_hashes(manifest)}
            candidate = staging / 'receipt.json'
            candidate.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            os.replace(candidate, receipt_path)
    except BaseException as original_error:
        try:
            for name in reversed(placed_new):
                shutil.rmtree(destination / name)
            for name in reversed(moved_old):
                os.replace(old_root / name, destination / name)
            if receipt_touched:
                if original_receipt is None:
                    if receipt_path.exists():
                        receipt_path.unlink()
                else:
                    receipt_path.write_bytes(original_receipt)
        except BaseException as rollback_error:
            raise RollbackIncomplete(
                f'preserve and inspect {staging}: {rollback_error}'
            ) from original_error
        try:
            shutil.rmtree(staging)
        except OSError:
            raise MutationRolledBack(original_error, staging) from original_error
        raise MutationRolledBack(original_error) from original_error
    # Receipt and directory moves are committed. Never roll back after disposal
    # has started: backups may already have been partly removed.
    try:
        shutil.rmtree(staging)
    except OSError as exc:
        return {'status': 'committed_cleanup_pending', 'cleanup_path': str(staging),
                'cleanup_error': f'{type(exc).__name__}: {exc}'}
    return {'status': 'committed', 'cleanup_path': None}


def main(argv: list[str] | None = None) -> int:
    """Resolve a project-local target and run preview/install/update/remove."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True, help='Existing Godot project directory')
    parser.add_argument('--host', choices=['codex', 'claude'], required=True)
    parser.add_argument('--dry-run', action='store_true', help='Validate and preview without project writes')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--update', action='store_true', help='Update unedited files owned by an existing receipt')
    group.add_argument('--uninstall', action='store_true', help='Remove only unedited files owned by this pack')
    args = parser.parse_args(argv)
    lock_path = None
    locked = False
    retain_lock = False
    try:
        project = args.project.expanduser().absolute()
        reject_symlinks(project)
        if not project.is_dir() or not (project / 'project.godot').is_file():
            raise ValueError('--project must be an existing directory with project.godot')
        project = project.resolve()
        if project == ROOT or project in ROOT.parents or ROOT in project.parents:
            raise ValueError('keep the source pack checkout separate from the target project')
        manifest = load_manifest(ROOT)
        host_dir = project / ('.agents' if args.host == 'codex' else '.claude')
        destination = host_dir / 'skills'
        action, old = preflight(destination, args.host, manifest, args.update, args.uninstall)
        if args.dry_run:
            print(json.dumps({'dry_run': True, 'action': action, 'destination': str(destination),
                              'skills': sorted(SKILLS)}, ensure_ascii=False, indent=2))
            return 0
        reject_symlinks(host_dir)
        host_dir.mkdir(parents=True, exist_ok=True)
        lock_path = host_dir / LOCK
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        locked = True
        with os.fdopen(descriptor, 'w') as lock:
            lock.write(f'pid={os.getpid()}\n')
        # The cooperative lock is held; verify the preflight snapshot again.
        action, old = preflight(destination, args.host, manifest, args.update, args.uninstall)
        outcome = {'status': 'unchanged', 'cleanup_path': None}
        if action != 'unchanged':
            outcome = mutate(destination, action, manifest, args.host)
        print(json.dumps({'action': action, 'destination': str(destination), 'version': manifest['version'], **outcome},
                         ensure_ascii=False))
        print('Review global/plugin/ancestor skills separately; this command never disables or removes them.')
        return 0
    except RollbackIncomplete as exc:
        retain_lock = True
        print(f'ROLLBACK INCOMPLETE (lock retained): {exc}', file=sys.stderr)
        return 3
    except MutationRolledBack as exc:
        print(json.dumps({'status': 'rolled_back', 'error': str(exc),
                          'cleanup_path': str(exc.cleanup_path) if exc.cleanup_path else None}), file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'INSTALL REFUSED (refused_before_change): {exc}', file=sys.stderr)
        return 2
    finally:
        if locked and not retain_lock and lock_path is not None:
            try:
                lock_path.unlink(missing_ok=True)
            except OSError as exc:
                print(f'LOCK CLEANUP PENDING: inspect {lock_path}: {exc}', file=sys.stderr)


if __name__ == '__main__':
    raise SystemExit(main())

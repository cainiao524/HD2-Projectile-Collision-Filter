"""Check or explicitly regenerate document_exports in this source checkout.

Edit docs/release first, then run --apply and review the generated differences.
No files are staged or committed. Previous destination bytes are backed up under
build/docs-sync-backup; independently edited tracked destinations are protected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bounded_path(root, name):
    if not isinstance(name, str) or not name or any(c in name for c in ('\\', ':', '\x00')):
        raise ValueError('Invalid document export path')
    if PurePosixPath(name).is_absolute() or any(part in ('', '.', '..') for part in name.split('/')):
        raise ValueError('Document export path must stay inside the source root')
    path = root / name
    if not path.resolve().is_relative_to(root):
        raise ValueError('Document export path escapes the source root: ' + name)
    current = root
    for part in PurePosixPath(name).parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Document export path uses a symlink or junction: ' + name)
    return path


def read_plan(root):
    root = Path(root).resolve()
    manifest_path = bounded_path(root, 'publication-files.json')
    mapping = json.loads(manifest_path.read_bytes()).get('document_exports')
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError('publication-files.json has no document_exports mapping')
    targets = list(mapping.values())
    if not all(isinstance(item, str) for item in targets):
        raise ValueError('Document export targets must be paths')
    if len({item.casefold() for item in targets}) != len(targets):
        raise ValueError('Duplicate document export destinations')
    if {item.casefold() for item in mapping} & {item.casefold() for item in targets}:
        raise ValueError('Document export destinations cannot overwrite export sources')
    plan = []
    for source, target in sorted(mapping.items()):
        if (any(PurePosixPath(name).suffix.lower() not in ('.md', '.bbcode') or '.git' in PurePosixPath(name).parts
                for name in (source, target))
                or PurePosixPath(source).suffix.lower() != PurePosixPath(target).suffix.lower()):
            raise ValueError('Document exports must preserve Markdown/BBCode extensions outside Git metadata')
        source_path = bounded_path(root, source)
        target_path = bounded_path(root, target)
        if not source_path.is_file():
            raise ValueError('Missing document source: ' + source)
        if target_path.exists() and not target_path.is_file():
            raise ValueError('Document destination is not a file: ' + target)
        desired = source_path.read_bytes()
        existing = target_path.read_bytes() if target_path.exists() else None
        plan.append({'source': source, 'target': target, 'desired': desired, 'existing': existing})
    return root, plan


def git_result(git_root, *args):
    return subprocess.run(['git', '-C', str(git_root), *args], capture_output=True, check=False)


def find_git_root(root):
    git_marker = any((parent / '.git').exists() for parent in (root, *root.parents))
    try:
        result = git_result(root, 'rev-parse', '--show-toplevel')
    except FileNotFoundError:
        if git_marker:
            raise ValueError('Git is required to protect tracked document destinations')
        return None
    if result.returncode:
        if git_marker:
            raise ValueError('Cannot inspect Git state; fix repository access before regenerating documents')
        return None
    return Path(result.stdout.decode().strip()).resolve()


def protect_tracked_destination(root, item, git_root):
    if git_root is None:
        return
    name = (root / item['target']).relative_to(git_root).as_posix()
    tracked = git_result(git_root, 'ls-files', '--stage', '-z', '--', name)
    if tracked.returncode:
        raise ValueError('Cannot inspect tracked destination: ' + item['target'])
    if not tracked.stdout:
        return
    if item['existing'] is None:
        raise ValueError('Tracked destination was independently deleted: ' + item['target'])
    head = git_result(git_root, 'rev-parse', 'HEAD:' + name)
    current = git_result(git_root, 'hash-object', '--path=' + name, '--', name)
    staged = git_result(git_root, 'diff', '--cached', '--quiet', 'HEAD', '--', name)
    if head.returncode or current.returncode or staged.returncode or current.stdout.strip() != head.stdout.strip():
        raise ValueError('Tracked destination has independent edits; review and resolve them first: ' + item['target'])


def sync_documents(root=ROOT, apply=False):
    root, plan = read_plan(root)
    changes = [item for item in plan if item['existing'] != item['desired']]
    result = {'operation': 'apply' if apply else 'check', 'in_sync': not changes,
              'updates': [{'source': item['source'], 'target': item['target'],
                           'status': 'missing' if item['existing'] is None else 'different'} for item in changes],
              'unchanged': len(plan) - len(changes), 'backup': None}
    if not apply or not changes:
        return result
    git_root = find_git_root(root)
    # Validate every target before writing any destination or backup.
    for item in changes:
        protect_tracked_destination(root, item, git_root)
    backup_root = bounded_path(root, 'build/docs-sync-backup')
    if backup_root.exists() and not backup_root.is_dir():
        raise ValueError('Document backup destination is not a directory')
    for item in plan:
        if bounded_path(root, item['source']).read_bytes() != item['desired']:
            raise ValueError('Document source changed during preflight; rerun the command')
        destination = bounded_path(root, item['target'])
        current = destination.read_bytes() if destination.exists() else None
        if current != item['existing']:
            raise ValueError('Document destination changed during preflight; rerun the command')
    backup_root.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix='sync-', dir=backup_root))
    records = []
    for item in changes:
        if item['existing'] is not None:
            copy = backup / 'previous' / item['target']
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_bytes(item['existing'])
        records.append({'source': item['source'], 'target': item['target'],
                        'previous_sha256': sha(item['existing']) if item['existing'] is not None else None,
                        'desired_sha256': sha(item['desired'])})
    (backup / 'sync-record.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for item in changes:
        destination = bounded_path(root, item['target'])
        current = destination.read_bytes() if destination.exists() else None
        if current != item['existing']:
            raise ValueError('Destination changed during regeneration; previous bytes are in ' + str(backup))
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(prefix='.p11-docs-', dir=destination.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(item['desired'])
            os.replace(temporary, destination)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    result['in_sync'] = True
    result['backup'] = backup.relative_to(root).as_posix()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Read-only check; exit 1 if generated aliases are stale (default)')
    mode.add_argument('--apply', action='store_true', help='Regenerate aliases, protect independent edits, and back up previous bytes')
    args = parser.parse_args(argv)
    try:
        result = sync_documents(apply=args.apply)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['in_sync'] else 1
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, 'Document sync failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())

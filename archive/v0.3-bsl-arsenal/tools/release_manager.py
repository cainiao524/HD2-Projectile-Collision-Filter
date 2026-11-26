"""Verify the two public ZIPs, explicitly publish a prerelease, or verify GitHub.

This tool never collects game data, stages commits, pushes Git, or deploys mods.
Only the ``publish`` command changes GitHub; it never edits existing releases.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import subprocess
import tempfile
import zipfile
import zlib

from build_variants_release import TOOLKIT_NAME, TOOLS, source_files, MOD_BUILDER, VERSION, SELECTABLE_NAME, CHOICES, ARCHIVE
SELECTABLE_GUID = MOD_BUILDER.GUID
from resource_archive import lua_resources

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = 'cainiao524/HD2-Projectile-Collision-Filter'
ACCEPTED_PAYLOADS = MOD_BUILDER.ACCEPTED_PAYLOADS
TEXT_SUFFIXES = {'.md', '.py', '.lua', '.json', '.cmd', '.txt', '.cjs', '.bbcode'}
SOURCE_PREFIX = 'Source/HD2-Projectile-Collision-Filter/'
SHA_MARKER = '<!-- p11-release-sha256 -->'
KNOWN_PUBLIC_IMAGES = {
    'docs/assets/projectile-collision-filter-cover.png': {
        'sha256': '1301416ebaefb64ecfa7f93ef62447d390a5a1ebb4603f8a1b9c1e0cd404b771',
        'width': 1672, 'height': 941,
    },
    'docs/assets/raise-weapon-aim-at-yourself-cover.png': {
        'sha256': 'eca99e4dfbf6207b46a0fa622eb08b98fd94648beee2ee8cfa7af0a3c7f033da',
        'width': 1672, 'height': 941,
    },
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_name(name):
    require(isinstance(name, str) and bool(name), 'Empty or non-text path')
    require('\\' not in name and ':' not in name and '\x00' not in name,
            'Unsafe path in release input')
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(p not in ('', '.', '..') for p in name.split('/')),
            'Unsafe path in release input')
    return path


def check_public_text(name, data):
    safe_name(name)
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('Non-text data in public source: ' + name) from exc
    require('\x00' not in text, 'Binary data in public text: ' + name)
    private = re.search(r'[A-Za-z]:[/\\](?:Users|File)[/\\]|gh[pous]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}',
                        text.replace('\\\\', '\\'))
    require(private is None, 'Private path or credential pattern in: ' + name)


def check_public_image(name, data):
    """Allow only reviewed artwork, with its exact identity and a valid PNG envelope."""
    safe_name(name)
    require(name in KNOWN_PUBLIC_IMAGES, 'Unapproved public image path: ' + name)
    expected = KNOWN_PUBLIC_IMAGES[name]
    require(len(data) <= 16 * 1024 * 1024 and data[:8] == b'\x89PNG\r\n\x1a\n',
            'Invalid public PNG signature or size: ' + name)
    at, chunks, ended = 8, [], False
    while at < len(data):
        require(at + 12 <= len(data), 'Truncated public PNG chunk: ' + name)
        length = struct.unpack_from('>I', data, at)[0]
        kind = data[at + 4:at + 8]
        end = at + 12 + length
        require(end <= len(data), 'Public PNG chunk exceeds file: ' + name)
        require(zlib.crc32(data[at + 4:end - 4]) == struct.unpack_from('>I', data, end - 4)[0],
                'Public PNG chunk CRC differs: ' + name)
        if not chunks:
            require(kind == b'IHDR' and length == 13, 'Public PNG must begin with IHDR: ' + name)
            width, height = struct.unpack_from('>II', data, at + 8)
            require((width, height) == (expected['width'], expected['height']),
                    'Public PNG dimensions differ: ' + name)
        else:
            require(kind != b'IHDR', 'Duplicate public PNG header: ' + name)
        chunks.append(kind)
        at = end
        if kind == b'IEND':
            require(length == 0 and at == len(data), 'Public PNG contains trailing data: ' + name)
            ended = True
            break
    require(ended and b'IDAT' in chunks, 'Public PNG lacks image data or IEND: ' + name)
    require(sha(data) == expected['sha256'], 'Reviewed public image SHA-256 differs: ' + name)


def check_source(files):
    require(bool(files), 'Public source set is empty')
    for name, data in files.items():
        path = safe_name(name)
        require(path.parts[0] not in ('research', 'work', 'vendor', 'diagnostics', 'build',
                                      'dist', 'publication', 'local-history', 'binaries', '.git'),
                'Private directory in public source: ' + name)
        if name in KNOWN_PUBLIC_IMAGES:
            check_public_image(name, data)
            continue
        require(path.suffix in TEXT_SUFFIXES or path.name in ('.gitignore', '.gitattributes'),
                'Forbidden public source file type: ' + name)
        check_public_text(name, data)


def asset_roles():
    # Fixed names from reviewed build code; never upload arbitrary manifest entries.
    return {SELECTABLE_NAME: 'selectable', TOOLKIT_NAME: 'toolkit'}


def read_zip(data, label):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)), 'Duplicate ZIP entries: ' + label)
            require(sum(item.file_size for item in archive.infolist()) <= 256 * 1024 * 1024,
                    'Unexpected expanded ZIP size: ' + label)
            for item in archive.infolist():
                safe_name(item.filename)
                require(not item.is_dir() and not stat.S_ISLNK(item.external_attr >> 16),
                        'Directory or symlink ZIP entry: ' + label)
                require(not item.flag_bits & 1, 'Encrypted ZIP entry: ' + label)
            require(archive.testzip() is None, 'ZIP integrity failure: ' + label)
            return {name: archive.read(name) for name in names}
    except zipfile.BadZipFile as exc:
        raise ValueError('Invalid ZIP: ' + label) from exc


def check_mod(entries, role):
    require(role == 'selectable', 'Only the integrated mod is public in this release')
    require('manifest.json' in entries, 'Mod has no Arsenal manifest')
    manifest = json.loads(entries['manifest.json'])
    require(manifest == MOD_BUILDER.selector_manifest(),
            'Bilingual selectable manifest, identity, exclusive choices or order differs')
    expected_entries = {'manifest.json', 'README.md', 'Source/payloads.json'}
    expected_payloads = {}
    for scope, folder, _, _, _ in CHOICES:
        prefix = 'Variants/' + folder
        archive = entries.get(prefix + '/' + ARCHIVE)
        require(archive is not None, 'Missing selected mod archive: ' + prefix)
        resources = list(lua_resources(io.BytesIO(archive), len(archive)))
        require(len(resources) == 1 and resources[0]['declaration'] == MOD_BUILDER.RESOURCE,
                'Unexpected resource identity in: ' + prefix)
        body = resources[0]['body']
        require(sha(body) == ACCEPTED_PAYLOADS[scope]['lua_sha256'],
                'Accepted unified runtime changed: ' + scope)
        require(sha(archive) == ACCEPTED_PAYLOADS[scope]['archive_sha256'],
                'Accepted game archive changed: ' + scope)
        for suffix in ('', '.stream', '.gpu_resources'):
            name = prefix + '/' + ARCHIVE + suffix
            expected_entries.add(name)
            require(name in entries, 'Missing resource payload: ' + name)
            if suffix:
                require(entries[name] == b'', 'Unexpected nonempty resource sidecar: ' + name)
        source, profile = MOD_BUILDER.bundle(scope)
        require(source == body, 'Published runtime differs from buildable source: ' + scope)
        for name, data in MOD_BUILDER.runtime_files(source, profile).items():
            target = 'Source/' + folder + '/' + name.removeprefix('Source/')
            expected_entries.add(target)
            require(entries.get(target) == data, 'Mod source/document differs: ' + target)
        expected_payloads[folder] = {'scope': scope, **ACCEPTED_PAYLOADS[scope]}
    require(json.loads(entries['Source/payloads.json']) == expected_payloads, 'Payload provenance differs')
    require(set(entries) == expected_entries, 'Unexpected mod file set')
    require(entries['README.md'] == MOD_BUILDER.canonical_public_bytes('README.md', (MOD_BUILDER.HERE / 'README.md').read_bytes()), 'Mod README differs')
    for name, data in entries.items():
        safe_name(name)
        if not name.startswith('Variants/'):
            require(PurePosixPath(name).suffix in {'.md', '.lua', '.json', '.py'}, 'Unexpected mod file: ' + name)
            check_public_text(name, data)


def check_toolkit(entries, files, report):
    roots = {'P11-Update.exe', 'Collect-HD2-Update.cmd', 'README.md', 'AGENTS.md',
             'LICENSE-NOTICE.md', 'MOD-SHA256SUMS.txt',
             'runtime-licenses/Python-LICENSE.txt', 'runtime-licenses/PyInstaller-COPYING.txt'}
    copies = {'tools/' + name for name in TOOLS}
    copies.update(name for name in files if name.startswith(('maintenance/', 'patches/')))
    expected = roots | copies | {SOURCE_PREFIX + name for name in files}
    require(set(entries) == expected, 'Toolkit files differ from the explicit public layout')
    require(entries['P11-Update.exe'].startswith(b'MZ'), 'Portable executable has no Windows PE header')
    for name, data in files.items():
        require(entries[SOURCE_PREFIX + name] == data, 'Toolkit source differs: ' + name)
    for name in copies:
        require(entries[name] == files[name], 'Toolkit runtime input differs: ' + name)
    for target, source in [('Collect-HD2-Update.cmd', 'Collect-HD2-Update.cmd'),
                           ('README.md', 'docs/COLLECTION.md'), ('LICENSE-NOTICE.md', 'LICENSE-NOTICE.md')]:
        require(entries[target] == files[source], 'Toolkit document/entry differs: ' + target)
    require(b'Source/HD2-Projectile-Collision-Filter/AGENTS.md' in entries['AGENTS.md'], 'Toolkit Agent entry is missing')
    mod_sums = ''.join(report['assets'][name]['sha256'] + '  ' + name + '\n'
                       for name in sorted(asset_roles()) if name != TOOLKIT_NAME)
    require(entries['MOD-SHA256SUMS.txt'].decode('ascii') == mod_sums,
            'Toolkit mod checksums differ from the integrated release mod')
    for name in roots - {'P11-Update.exe'}:
        check_public_text(name, entries[name])


def verify_release(release_dir):
    release_dir = Path(release_dir).resolve()
    report = json.loads((release_dir / 'PUBLIC-ASSETS.json').read_bytes())
    require(report.get('project') == 'HD2-Projectile-Collision-Filter' and report.get('release') == VERSION,
            'Release manifest is not for the current build code')
    require(report.get('prerelease') is True, 'This release must remain a prerelease')
    names = report.get('public_assets', [])
    roles = asset_roles()
    require(len(roles) == 2 and isinstance(names, list) and len(names) == 2
            and set(names) == set(roles) and set(report.get('assets', {})) == set(roles),
            'Release must contain exactly the two approved ZIP assets')
    files = source_files()
    check_source(files)
    require(report.get('source_manifest') == {name: sha(data) for name, data in files.items()},
            'Built source snapshot differs from current exportable source; rebuild the release')
    contents = {}
    for name in names:
        require(safe_name(name).name == name and name.endswith('.zip'), 'Unsafe asset filename')
        path = release_dir / name
        require(path.resolve().parent == release_dir and not path.is_symlink(), 'Asset escapes release directory')
        data = path.read_bytes()
        metadata = report['assets'][name]
        require(metadata.get('bytes') == len(data) and metadata.get('sha256') == sha(data),
                'Asset size or SHA-256 mismatch: ' + name)
        contents[name] = read_zip(data, name)
        if roles[name] != 'toolkit':
            check_mod(contents[name], roles[name])
    check_toolkit(contents[TOOLKIT_NAME], files, report)
    return report


def run(*args, cwd=None):
    result = subprocess.run(list(args), cwd=cwd, capture_output=True, check=False)
    require(result.returncode == 0, args[0] + ' failed (exit ' + str(result.returncode)
            + '); check authentication, repository access, and command prerequisites')
    return result.stdout


def gh_json(*args):
    return json.loads(run('gh', *args))


def check_repository(repo):
    require(re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo) is not None, 'Use owner/repository format')


def check_target(target):
    require(isinstance(target, str) and re.fullmatch(r'[0-9a-f]{40}', target) is not None,
            'Use a full lowercase 40-character commit SHA for --target')


def check_git_source(git_dir, target, report):
    check_target(target)
    git_dir = Path(git_dir).resolve()
    def git(*args):
        return run('git', '-C', str(git_dir), *args)
    require(Path(git('rev-parse', '--show-toplevel').decode().strip()).resolve() == git_dir,
            '--git-dir must be the public source repository root')
    require(git('rev-parse', 'HEAD').decode().strip() == target, 'Publish target differs from local HEAD')
    require(not git('status', '--porcelain', '--untracked-files=normal').strip(),
            'Public source checkout has uncommitted or untracked files')
    tracked = set(git('ls-tree', '-r', '--name-only', '-z', target).decode().rstrip('\x00').split('\x00'))
    require(tracked == set(report['source_manifest']), 'Commit file set differs from the public source allowlist')
    for name, digest in report['source_manifest'].items():
        path = git_dir / name
        require(path.resolve().is_relative_to(git_dir) and not path.is_symlink(), 'Source path escapes checkout')
        require(sha(path.read_bytes()) == digest, 'Committed checkout differs from packaged source: ' + name)
        # Compare Git's canonical clean-filtered blobs as well as the exact ZIP
        # input bytes above. Checkout line endings may differ from blob bytes.
        require(git('hash-object', '--path=' + name, '--', name).strip()
                == git('rev-parse', target + ':' + name).strip(),
                'Commit blob differs from packaged source: ' + name)


def notes_with_hashes(notes, report):
    check_public_text('release-notes.md', notes.encode('utf-8'))
    require(SHA_MARKER not in notes, 'Remove the generated checksum section before publishing')
    table = '\n\n' + SHA_MARKER + '\n### SHA-256\n\n| File | SHA-256 |\n|---|---|\n'
    return notes.rstrip() + table + ''.join('| `' + name + '` | `' + report['assets'][name]['sha256']
                                           + '` |\n' for name in report['public_assets'])


def publish_release(release_dir, repo, target, notes, git_dir=ROOT):
    check_repository(repo)
    report = verify_release(release_dir)
    check_git_source(git_dir, target, report)
    commit = gh_json('api', f'repos/{repo}/commits/{target}')
    require(commit.get('sha') == target, 'Target commit is not available on GitHub; push it first')
    refs = gh_json('api', f'repos/{repo}/git/matching-refs/tags/{report["release"]}')
    if any(ref.get('ref') == 'refs/tags/' + report['release'] for ref in refs):
        existing = gh_json('api', f'repos/{repo}/commits/{report["release"]}')
        require(existing.get('sha') == target, 'Existing release tag points to a different commit')
    body = notes_with_hashes(Path(notes).read_text(encoding='utf-8-sig'), report)
    with tempfile.TemporaryDirectory(prefix='p11-release-notes-') as temporary:
        notes_path = Path(temporary) / 'release.md'
        notes_path.write_text(body, encoding='utf-8', newline='\n')
        paths = [str((Path(release_dir) / name).resolve()) for name in report['public_assets']]
        url = run('gh', 'release', 'create', report['release'], *paths, '--repo', repo,
                  '--target', target, '--title', 'Projectile Collision Filter ' + report['release'] + ' — P-11 Self-Heal / 自療・四選一',
                  '--notes-file', str(notes_path), '--prerelease').decode().strip()
    return {'operation': 'publish', 'release': report['release'], 'release_url': url,
            'target': target, 'assets': len(paths), 'prerelease': True,
            'next': 'Run verify-remote --target with the same commit SHA.'}


def verify_remote(release_dir, repo, target):
    check_repository(repo)
    check_target(target)
    report = verify_release(release_dir)
    release = gh_json('api', f'repos/{repo}/releases/tags/{report["release"]}')
    require(release.get('prerelease') is True and release.get('draft') is False,
            'Remote release must be a published prerelease')
    require(release.get('tag_name') == report['release'], 'Remote tag differs')
    commit = gh_json('api', f'repos/{repo}/commits/{report["release"]}')
    require(commit.get('sha') == target, 'Remote release tag points to a different commit')
    items = release.get('assets', [])
    assets = {item['name']: item for item in items}
    require(len(items) == 2 and set(assets) == set(report['public_assets']), 'Remote asset set differs')
    for name, metadata in report['assets'].items():
        item = assets[name]
        require(item.get('state') == 'uploaded' and item.get('size') == metadata['bytes'],
                'Remote asset is incomplete or size differs: ' + name)
        if item.get('digest'):
            require(item['digest'] == 'sha256:' + metadata['sha256'], 'Remote asset SHA-256 differs: ' + name)
        require(isinstance(item.get('id'), int), 'Remote asset ID missing: ' + name)
        data = run('gh', 'api', '-H', 'Accept: application/octet-stream',
                   f'repos/{repo}/releases/assets/{item["id"]}')
        require(len(data) == metadata['bytes'] and sha(data) == metadata['sha256'],
                'Downloaded asset size or SHA-256 differs: ' + name)
    return {'operation': 'verify-remote', 'release': report['release'], 'target': target,
            'release_url': release['html_url'], 'assets': 2, 'sha256_verified': True,
            'new_gameplay_verified': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('verify', 'publish', 'verify-remote'):
        child = sub.add_parser(command)
        child.add_argument('--release-dir', type=Path, default=ROOT / 'dist/release')
        child.add_argument('--repo', default=DEFAULT_REPO)
        if command != 'verify':
            child.add_argument('--target', required=True, help='Full commit SHA; never a moving branch name')
        if command == 'publish':
            child.add_argument('--notes', type=Path, required=True)
            child.add_argument('--git-dir', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        if args.command == 'verify':
            report = verify_release(args.release_dir)
            result = {'operation': 'verify', 'release': report['release'], 'assets': 2,
                      'source_files': len(report['source_manifest']), 'sha256_verified': True,
                      'new_gameplay_verified': False}
        elif args.command == 'publish':
            result = publish_release(args.release_dir, args.repo, args.target, args.notes, args.git_dir)
        else:
            result = verify_remote(args.release_dir, args.repo, args.target)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        parser.exit(1, 'Release check failed: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()

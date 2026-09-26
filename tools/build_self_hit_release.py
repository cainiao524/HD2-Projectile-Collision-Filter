"""Build the standalone self-hit release from an explicit source allowlist."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist/release'
NAME = 'P11-Self-Hit-DataOnly-0.2.1-build25480438.zip'
EXPECTED = '73c8c1e85b9732b85e0324b45b19d2c8b6c104abcd394c0f82ac49b67f9da8c2'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def zip_files(path, files):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 9, 26, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP integrity check failed')


def source_files():
    allow = json.loads((ROOT / 'publication-files.json').read_bytes())
    paths = [ROOT / name for name in allow['files']]
    for folder, suffixes in allow['folders'].items():
        paths += [p for p in (ROOT / folder).rglob('*') if p.is_file()
                  and p.suffix in suffixes and '__pycache__' not in p.parts]
    files = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in paths}
    for source, destination in allow['document_exports'].items():
        files[destination] = (ROOT / source).read_bytes()
    # Preserve only the self-hit record in the shared local maintenance metadata.
    baselines = json.loads(files['maintenance/baselines.json'])
    for baseline in baselines['baselines']:
        baseline['components'] = {'self_heal': baseline['components']['self_heal']}
        baseline['components']['self_heal']['verification_scope'] = (
            '2026-09-26: user confirmed basic self-hit healing on build 25480438. '
            'Full host/client, timing and slot-concurrency coverage remains incomplete.')
    files['maintenance/baselines.json'] = (json.dumps(baselines, ensure_ascii=False, indent=2) + '\n').encode()
    mapping = json.loads(files['maintenance/porting-map.json'])
    mapping = {k: mapping[k] for k in ('schema_version', 'reference_build', 'scope', 'self_hit')}
    files['maintenance/porting-map.json'] = (json.dumps(mapping, ensure_ascii=False, indent=2) + '\n').encode()
    manifest = json.loads(files['patches/25480438/manifest.json'])
    loader = {k: manifest['loader'][k] for k in ('public_release', 'internal_min', 'api')}
    manifest = {'schema_version': 1, 'id': '25480438-self-hit-0.2.1', 'status': 'unverified',
                'target': manifest['target'], 'loader': loader,
                'features': [{'id': 'self_heal', 'source': 'mods/p11_self_hit_dataonly/core.lua',
                              'status': 'disabled', 'user_confirmed_working': True,
                              'reason': 'Basic behavior confirmed; offline identity never auto-enables gameplay.'}]}
    files['patches/25480438/manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    return files


def export_source(files):
    target = ROOT / 'publication/P11-Enhanced'
    state = target.parent / 'self-hit-exported-hashes.json'
    previous = json.loads(state.read_bytes()) if state.is_file() else {}
    target.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        path = target / name
        if path.exists() and sha(path.read_bytes()) not in (previous.get(name), sha(data)):
            raise ValueError('Export contains independent edits: ' + name)
    for name, data in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    state.write_text(json.dumps({n: sha(d) for n, d in files.items()}, indent=2) + '\n', encoding='utf-8')
    return target


def build():
    original = ROOT / 'dist' / NAME
    if not original.is_file():
        subprocess.run([sys.executable, str(ROOT / 'mods/p11_self_hit_dataonly/build.py')], check=True)
    data = original.read_bytes()
    if sha(data) != EXPECTED:
        raise ValueError('The tested self-hit ZIP changed; refusing to publish it under the same identity')
    DIST.mkdir(parents=True, exist_ok=True)
    files = source_files()
    export_source(files)
    (DIST / NAME).write_bytes(data)
    source_name = 'P11-Self-Hit-Source-v0.2.1.zip'
    zip_files(DIST / source_name, {'P11-Enhanced/' + n: d for n, d in files.items()})
    assets = [NAME, source_name]
    (DIST / 'SHA256SUMS.txt').write_text(''.join(
        sha((DIST / n).read_bytes()) + '  ' + n + '\n' for n in assets), encoding='ascii')
    assets.append('SHA256SUMS.txt')
    report = {'project': 'P11-Enhanced', 'scope': 'standalone P-11 self-hit healing only',
              'release': 'v0.2.1', 'public_assets': assets, 'published': False,
              'self_hit_original_preserved': True, 'self_hit_basic_user_confirmed': True,
              'source_files': len(files), 'source_manifest': {n: sha(d) for n, d in files.items()},
              'assets': {n: {'sha256': sha((DIST / n).read_bytes()), 'bytes': (DIST / n).stat().st_size}
                         for n in assets}}
    (DIST / 'PUBLIC-ASSETS.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'source_manifest'}, indent=2))
    return report


if __name__ == '__main__':
    build()

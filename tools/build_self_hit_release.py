"""Shared deterministic packaging and guarded source export helpers."""
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


# Match .gitattributes without requiring Git in the portable source toolkit.
# Historical -text inputs are deliberately exempt: they preserve old ZIP bytes.
VERBATIM_PUBLIC_FILES = frozenset({
    'mods/p11_self_hit_dataonly/README-zh-TW.md',
    'mods/p11_self_hit_dataonly/VALIDATION.md',
    'mods/p11_self_hit_dataonly/profile.json',
    'mods/weapon_self_hit_candidate/README-zh-TW.md',
    'mods/weapon_self_hit_candidate/VALIDATION.md',
})


def canonical_public_bytes(name, data):
    """Canonical checkout bytes for public source/package copies, not runtime data."""
    if name in VERBATIM_PUBLIC_FILES or Path(name).suffix.lower() in ('.png', '.zip', '.exe'):
        return data
    normalized = data.replace(b'\r\n', b'\n')
    return normalized.replace(b'\n', b'\r\n') if Path(name).suffix.lower() == '.cmd' else normalized


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
    from build_variants_release import source_files as selected
    return selected()


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
    from build_variants_release import build as build_all
    return build_all()


if __name__ == '__main__':
    build()

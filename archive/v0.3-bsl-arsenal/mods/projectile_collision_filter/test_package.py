"""Inspect the built public integrated ZIP without executing native addon code."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile
from lupa.luajit21 import LuaRuntime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from resource_archive import lua_resources

spec = importlib.util.spec_from_file_location('public_unified_builder', HERE / 'build.py')
BUILDER = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BUILDER)
OUT = ROOT / 'dist'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    path = OUT / BUILDER.NAME
    assert path.is_file(), 'Run python tools/build_release.py --mods-only first'
    shared_core = ('local Core=(function()\n' + (HERE / 'core.lua').read_text(encoding='utf-8') + '\nend)()\n').encode()
    compile_only = LuaRuntime(encoding=None).eval(b'function(s) return assert(loadstring(s)) end')
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(set(z.namelist()))
        for name in z.namelist():
            assert not name.startswith(('/', '\\')) and '..' not in Path(name).parts
            assert Path(name).suffix.lower() not in ('.exe', '.dll', '.bin', '.log'), name
        manifest = json.loads(z.read('manifest.json'))
        assert manifest == BUILDER.selector_manifest()
        for scope, folder, _, label, _ in BUILDER.CHOICES:
            raw = z.read('Variants/' + folder + '/' + BUILDER.ARCHIVE)
            expected = BUILDER.ACCEPTED_PAYLOADS[scope]
            assert sha(raw) == expected['archive_sha256'], scope
            resource, = list(lua_resources(io.BytesIO(raw), len(raw)))
            assert resource['declaration'] == BUILDER.RESOURCE
            body = resource['body']
            assert sha(body) == expected['lua_sha256'], scope
            assert body.count(shared_core) == 1
            assert body.count(b'local Core=(function()') == 1
            assert body.count(b'kernel.WriteProcessMemory(process,ptr(at),desired,2,got)') == 1
            assert b'for slot=0,2047 do' not in body
            assert b'VirtualProtect' not in body and b'CreateRemoteThread' not in body
            assert compile_only(body) is not None
            assert z.read('Source/' + folder + '/projectile_collision_filter.lua') == body
            p = json.loads(z.read('Source/' + folder + '/profile.json'))
            assert p['scope'] == scope
            assert len(p['code_anchors']) == 12 and len(p['cursor_anchors']) == 3
            assert p['gameplay_verified'] is False  # Original serialized profile is immutable.
            assert p['exclude_shotguns'] == (scope != 'native_weapons')
    originals = {
        'dist/P11-Self-Hit-DataOnly-0.2.1-build25480438.zip': '73c8c1e85b9732b85e0324b45b19d2c8b6c104abcd394c0f82ac49b67f9da8c2',
        'dist/candidates/cursor-0.2.3/P11-Self-Hit-DataOnly-0.2.3-CURSOR-CANDIDATE-build25480438.zip': 'aad662fcdab09699adce96382204f9e5adb76eb72e823f02aeaff0a8ab54f1e7',
        'dist/candidates/v0.3.0-preview.8/Projectile-Collision-Filter-v0.3.0-preview.8-build25480438-CANDIDATE.zip': BUILDER.ACCEPTED_CANDIDATE_SHA256,
    }
    present = {}
    for name, expected in originals.items():
        if (ROOT / name).exists():
            assert sha((ROOT / name).read_bytes()) == expected, name
            present[name] = expected
    result = {'package_count': 1, 'exclusive_scopes': [c[3] for c in BUILDER.CHOICES],
              'one_addon_per_choice': True, 'shared_core_identical': True,
              'accepted_candidate_payloads_preserved': True, 'lua_compile_only': True,
              'historical_packages_present_and_unchanged': present, 'native_execution': False,
              'sha256': {path.name: sha(path.read_bytes())}}
    (OUT / 'PACKAGE-CHECK-preview8.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

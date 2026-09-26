"""Run offline LuaJIT integration regressions; never open a live game process.

Run from project root: python mods/projectile_collision_filter/test_runtime.py
Requires requirements-dev.txt. Fixtures and Windows APIs are synthetic.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from lupa.luajit21 import LuaRuntime

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'p11_self_hit_dataonly'
spec = importlib.util.spec_from_file_location('unified_runtime_test_builder', HERE / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def runtime():
    rt = LuaRuntime(encoding=None, unpack_returned_tuples=True)
    source = (HERE / 'core.lua').read_bytes()
    rt.globals()[b'NewCore'] = rt.eval(b'function(s) return function() return assert(loadstring(s))() end end')(source)
    rt.globals()[b'Fixture'] = rt.execute((HERE / 'test_fixture.lua').read_bytes())
    rt.globals()[b'TestProfiles'] = rt.eval(builder.lua({s: builder.profile(s) for s in builder.SCOPES}).encode())
    return rt


def writer_regression():
    rt = runtime()
    rt.execute(b'''
        local instances={}
        Core={tick=function(api)
            instances[api]=instances[api] or NewCore()
            return instances[api].tick(api,TestProfiles.p11)
        end}
    ''')
    rt.globals()[b'MakeData'] = rt.execute((HERE / 'data_windows.lua').read_bytes())
    return int(rt.execute((ORIGINAL / 'test_data_windows.lua').read_bytes()))


def version_regression():
    rt = runtime()
    rt.globals()[b'Version'] = rt.execute((HERE / 'version.lua').read_bytes())
    return int(rt.execute(b'''
        local checks=0
        local function check(x,why) checks=checks+1; assert(x,why) end
        for _,scope in ipairs({'p11','pistols','native_no_shotguns','native_weapons'}) do
            local p=TestProfiles[scope]
            local map={}
            for _,list in ipairs({p.code_anchors,p.cursor_anchors}) do
                for _,a in ipairs(list) do
                    map[a.rva]=a.bytes_hex:gsub('..',function(x) return string.char(tonumber(x,16)) end)
                end
            end
            local api={read=function(rva,n) local v=map[rva]; assert(v and #v==n); return v end,
                file_hashes=function() return {game_sha256=p.game_sha256,exe_sha256=p.exe_sha256} end}
            check(pcall(Version.files,api,p),'matching disk hashes pass')
            check(pcall(Version.anchors,api,p),'all 12 base and 3 cursor anchors pass')
            for _,list in ipairs({p.code_anchors,p.cursor_anchors}) do
                for _,a in ipairs(list) do
                    local bytes=map[a.rva]; map[a.rva]=string.rep('\0',#bytes)
                    check(not pcall(Version.anchors,api,p),'each changed code/cursor anchor fails closed')
                    map[a.rva]=bytes
                end
            end
            api.file_hashes=function() return {game_sha256='different',exe_sha256=p.exe_sha256} end
            check(not pcall(Version.files,api,p),'changed game DLL fails closed')
            api.file_hashes=function() return {game_sha256=p.game_sha256,exe_sha256='different'} end
            check(not pcall(Version.files,api,p),'changed executable fails closed')
        end
        return checks
    '''))


def main():
    results = {}
    for scope in builder.SCOPES:
        source, _ = builder.bundle(scope)
        rt = LuaRuntime(encoding=None)
        assert rt.eval(b'function(s) return assert(loadstring(s)) end')(source)
        results[scope + '_bundle_compiles'] = True
    rt = runtime()
    results['integrated_runtime_assertions'] = int(rt.execute((HERE / 'test_runtime.lua').read_bytes()))
    results['unchanged_windows_writer_assertions'] = writer_regression()
    results['version_assertions'] = version_regression()
    rt = runtime()
    rt.globals()[b'Entry'] = rt.execute((HERE / 'entry.lua').read_bytes())
    rt.globals()[b'LegacyEntry'] = rt.execute((ORIGINAL / 'entry.lua').read_bytes())
    rt.globals()[b'Profile'] = rt.globals()[b'TestProfiles'][b'p11']
    results['entry_assertions'] = int(rt.execute((HERE / 'test_entry.lua').read_bytes()))
    for name in ('data_windows.lua', 'image_windows.lua'):
        assert (HERE / name).read_bytes() == (ORIGINAL / name).read_bytes(), name + ' changed'
    print(json.dumps({'results': results, 'native_execution': False, 'gameplay_verified': False,
                      'legacy_core_fixture_note': 'The legacy full-sweep fixture reuses retired slots without advancing the allocator. Its identity/ownership assertions are independently covered with cursor-aware fixtures; the original writer test is run unchanged.'}, indent=2))


if __name__ == '__main__':
    main()

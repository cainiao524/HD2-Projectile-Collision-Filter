"""Isolated LuaJIT fixture tests; never load or execute the Windows addon."""
import json
from pathlib import Path
from lupa.luajit21 import LuaRuntime
from build import bundle, profile, SCOPES
from build import lua

HERE = Path(__file__).resolve().parent
results = {}
for scope in SCOPES:
    source, p = bundle(scope)
    rt = LuaRuntime(encoding=None)
    assert rt.eval(b'function(s) return assert(loadstring(s)) end')(source)
    results[scope + '_compile'] = True
for name, file in [('Core', 'core.lua'), ('Fixture', 'test_fixture.lua')]:
    rt.globals()[name.encode()] = rt.execute((HERE / file).read_bytes())
rt.globals()[b'TestProfiles']=rt.eval(lua({s:profile(s) for s in SCOPES}).encode())
rt.execute(b'''function TestProfile(scope)
    local out={};for k,v in pairs(TestProfiles[scope]) do out[k]=v end
    out.pistol_unit_hashes={'05e4e5c2db6e44a2'}
    return out
end''')
results['core_assertions'] = rt.execute((HERE / 'test_core.lua').read_bytes())
results['filtering_assertions'] = rt.execute((HERE / 'test_filtering.lua').read_bytes())
results['shotgun_assertions'] = rt.execute((HERE / 'test_shotguns.lua').read_bytes())
entry_rt = LuaRuntime(encoding=None)
entry_rt.globals()[b'Entry'] = entry_rt.execute((HERE / 'entry.lua').read_bytes())
# Build the exact Lua profile literal used by the bundle.
entry_rt.globals()[b'Profile'] = entry_rt.eval(lua(profile('pistols')).encode())
results['entry_assertions'] = entry_rt.execute((HERE / 'test_entry.lua').read_bytes())
combined=LuaRuntime(encoding=None)
combined.globals()[b'Entry']=combined.execute((HERE/'entry.lua').read_bytes())
combined.globals()[b'P11Entry']=combined.execute((HERE.parent/'p11_self_hit_dataonly/entry.lua').read_bytes())
results['combined_callback_assertions']=combined.execute((HERE/'test_combined.lua').read_bytes())
assert len(profile('pistols')['pistol_unit_hashes']) == 8
print(json.dumps({'results': results, 'native_execution': False, 'gameplay_verified': False}, indent=2))

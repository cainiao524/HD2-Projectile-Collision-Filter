from pathlib import Path
import io,json,zipfile,sys
ROOT=Path(__file__).resolve().parents[1]
SCOPES={'p11':'P11','pistols':'Pistols','native_no_shotguns':'NativeNoShotguns','native_weapons':'NativeWeapons'}
VERSION='0.3.2-bsl-four'; GUID='f344360d-eb4a-4baa-b631-8e6982ecd9fb'; RESOURCE='mods/pcf/bsl_four_scope_self_hit'

def main():
    profiles={s:json.loads((ROOT/'Source/profiles'/(s+'.json')).read_text(encoding='utf-8')) for s in SCOPES}
    for s,p in profiles.items():
        assert p['scope']==s and p['version']==VERSION and p['resource']==RESOURCE and p['manager_guid']==GUID
        assert p['loader']=={'api':1,'internal_min':16,'internal_max':17,'public_release_recommended':'v18'}
        assert p['native_patch'] is False and p['native_hook'] is False and p['update_hook'] is True
    assert profiles['p11']['projectile_type']==318
    runtime=''.join((ROOT/'Source/runtime'/name).read_text(encoding='utf-8') for name in ('core.lua','version.lua','image_windows.lua','data_windows.lua','entry.lua'))
    for token in ('VirtualProtect','FlushInstructionCache','VirtualAlloc','CreateRemoteThread'):
        assert token not in runtime
    from lupa.luajit21 import LuaRuntime
    rt=LuaRuntime(encoding=None)
    for s in SCOPES:
        bundle=(ROOT/'Source/bundles'/(s+'.lua')).read_bytes()
        ok,err=rt.eval(b'function(s)local f,e=loadstring(s);return f~=nil,e end')(bundle); assert ok,(s,err)
    zips=list((ROOT/'dist').glob('Projectile-Collision-Filter-BSL-Four-*.zip')); assert len(zips)==1,zips
    with zipfile.ZipFile(zips[0]) as z:
        assert z.testzip() is None
        manifest=json.loads(z.read('manifest.json')); assert len(manifest['Options'][0]['SubOptions'])==4
        sys.path.insert(0,str(ROOT/'tools')); from resource_archive import lua_resources
        for s,folder in SCOPES.items():
            raw=z.read(f'Variants/{folder}/9ba626afa44a3aa3.patch_0')
            rows=list(lua_resources(io.BytesIO(raw),len(raw))); assert len(rows)==1 and rows[0]['declaration']==RESOURCE
    print('current four-scope package smoke ok')
if __name__=='__main__': main()

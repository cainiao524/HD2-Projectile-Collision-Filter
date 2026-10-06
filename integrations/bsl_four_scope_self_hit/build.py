from __future__ import annotations
import hashlib, io, json, zipfile
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
from resource_archive import make_archive, lua_resources
VERSION='0.3.2-bsl-four'; BUILD=25480438; GUID='f344360d-eb4a-4baa-b631-8e6982ecd9fb'; RESOURCE='mods/pcf/bsl_four_scope_self_hit'; ARCHIVE='9ba626afa44a3aa3.patch_0'
SCOPES={'p11':'P11','pistols':'Pistols','native_no_shotguns':'NativeNoShotguns','native_weapons':'NativeWeapons'}
RUNTIME=('core.lua','version.lua','image_windows.lua','data_windows.lua','entry.lua')

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def jbytes(value)->bytes:return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def lua(v):
    if v is True:return 'true'
    if v is False:return 'false'
    if v is None:return 'nil'
    if isinstance(v,str):return json.dumps(v,ensure_ascii=True)
    if isinstance(v,(int,float)):return str(v)
    if isinstance(v,list):return '{'+','.join(lua(x) for x in v)+'}'
    if isinstance(v,dict):return '{'+','.join('['+lua(k)+']='+lua(vv) for k,vv in sorted(v.items(),key=lambda kv:str(kv[0])))+'}'
    raise TypeError(type(v))
def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def compile_lua(src:bytes):
    from lupa.luajit21 import LuaRuntime
    rt=LuaRuntime(encoding=None)
    ok,err=rt.eval(b'function(s)local f,e=loadstring(s);return f~=nil,e end')(src)
    require(ok,'LuaJIT compile failed: '+str(err))
    return rt.eval(b'jit.version').decode()
def runtime_profile(profile:dict)->dict:
    # JSON object keys are strings; the Lua runtime compares projectile type
    # numbers, so convert the exclusion table keys before embedding it.
    q=json.loads(json.dumps(profile))
    q['excluded_projectile_types']={int(k):v for k,v in q.get('excluded_projectile_types',{}).items()}
    return q

def assemble(profile:dict)->bytes:
    modules=[]
    for symbol,name in zip(('Core','Version','MakeImage','MakeData','Entry'),RUNTIME):
        body=(ROOT/'Source/runtime'/name).read_text(encoding='utf-8')
        modules.append('local '+symbol+'=(function()\n'+body+'\nend)()\n')
    src=('-- HD2-Addon: '+RESOURCE+'\n'+''.join(modules)+'return Entry(Core,Version,MakeImage,MakeData,'+lua(runtime_profile(profile))+',_G)\n').encode()
    compile_lua(src); return src
def build():
    profiles={s:json.loads((ROOT/'Source/profiles'/f'{s}.json').read_text(encoding='utf-8')) for s in SCOPES}
    for scope,p in profiles.items():
        require(p['version']==VERSION and p['resource']==RESOURCE and p['manager_guid']==GUID,'profile identity '+scope)
        require(p['build_id']==BUILD and p['loader']=={'api':1,'internal_min':16,'internal_max':17,'public_release_recommended':'v18'},'profile loader/build '+scope)
        require(p.get('native_patch') is False and p.get('native_hook') is False and p.get('update_hook') is True,'native policy '+scope)
        require(p['scope']==scope,'scope mismatch '+scope)
        require(len(p.get('code_anchors',[]))==12 and len(p.get('cursor_anchors',[]))==3 and len(p.get('research_anchors',[]))==8,'anchor coverage '+scope)
    files={}
    for name in RUNTIME: files['Source/runtime/'+name]=(ROOT/'Source/runtime'/name).read_bytes()
    files['Source/profile.json']=(ROOT/'Source/profile.json').read_bytes()
    for scope in SCOPES:
        files['Source/profiles/'+scope+'.json']=(ROOT/'Source/profiles'/(scope+'.json')).read_bytes()
    for path in (ROOT/'Source/reference').rglob('*'):
        if path.is_file(): files[path.relative_to(ROOT).as_posix()]=path.read_bytes()
    variants={}; jit=''
    for scope,folder in SCOPES.items():
        src=assemble(profiles[scope]); jit='LuaJIT 2.1'
        (ROOT/'Source/bundles').mkdir(exist_ok=True); (ROOT/'Source/bundles'/f'{scope}.lua').write_bytes(src)
        archive=make_archive(RESOURCE,src)
        parsed=list(lua_resources(io.BytesIO(archive),len(archive)))
        require(len(parsed)==1 and parsed[0]['declaration']==RESOURCE and parsed[0]['body']==src,'archive roundtrip '+scope)
        vdir=ROOT/'Variants'/folder; vdir.mkdir(parents=True,exist_ok=True)
        for suffix,data in (('',archive),('.stream',b''),('.gpu_resources',b'')):
            (vdir/(ARCHIVE+suffix)).write_bytes(data)
        files['Source/bundles/'+scope+'.lua']=src
        files['Variants/'+folder+'/'+ARCHIVE]=archive
        files['Variants/'+folder+'/'+ARCHIVE+'.stream']=b''
        files['Variants/'+folder+'/'+ARCHIVE+'.gpu_resources']=b''
        variants[scope]={'folder':'Variants/'+folder,'profile':'Source/profiles/'+scope+'.json','bundle':'Source/bundles/'+scope+'.lua','profile_sha256':sha(files['Source/profiles/'+scope+'.json']),'bundle_sha256':sha(src),'archive_sha256':sha(archive)}
    desc=('BSL Lua-only four-scope candidate for build 25480438. No game.dll code patch or native hook; cursor delta/type prefilter, local-owner guards, and bounded per-update budgets. Choose exactly one scope. Shotgun scope is bounded but may defer bursts; gameplay/performance remain unverified. / 纯 BSL Lua 四范围候选，不修改 game.dll、不安装 native hook；使用 cursor 增量、type 预筛选、本机 owner 校验和有界更新预算。四选一；含霰弹范围有界但可能延迟 burst，玩法与性能仍未验证。')
    manifest={'Version':1,'Guid':GUID,'Name':'Projectile Collision Filter BSL Four Scope','Description':desc,'Options':[{'Name':'Effect Scope / 生效范围','Description':desc,'SubOptions':[{'Name':({'p11':'P-11 Only / 仅治疗手枪','pistols':'All Sidearms / 全部手枪','native_no_shotguns':'Native Weapons No Shotguns / 原生武器排除霰弹','native_weapons':'Native Weapons Including Shotguns / 原生武器包含霰弹'}[s]),'Description':desc,'Include':['Variants/'+f]} for s,f in SCOPES.items()]}]}
    files['manifest.json']=jbytes(manifest)
    files['package-info.json']=jbytes({'version':VERSION,'guid':GUID,'resource':RESOURCE,'archive':ARCHIVE,'build_id':BUILD,'loader':profiles['p11']['loader'],'variants':variants,'native_patch':False,'native_hook':False,'update_hook':True,'per_projectile_processing':True,'performance_policy':'scope-specific bounded cursor/type-prefilter; no zero-overhead guarantee','gameplay_verified':False,'performance_gameplay_verified':False,'luajit_compile_runtime':jit})
    (ROOT/'manifest.json').write_bytes(files['manifest.json'])
    (ROOT/'package-info.json').write_bytes(files['package-info.json'])
    for path in ('README.zh-CN.md','README.zh-TW.md','BUILDING.md','VALIDATION.md','TEST_PLAN.zh-CN.md','package-config.json'):
        files[path]=(ROOT/path).read_bytes()
    # add a compact source integrity manifest after all payloads are known
    files['Source/source-integrity.json']=jbytes({k:sha(v) for k,v in sorted(files.items()) if k.startswith('Source/')})
    target=ROOT/'dist'/f'Projectile-Collision-Filter-BSL-Four-{VERSION}-build{BUILD}.zip'; target.parent.mkdir(exist_ok=True)
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(files):
            info=zipfile.ZipInfo(name,(2026,10,5,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16; z.writestr(info,files[name])
    payload=out.getvalue(); target.write_bytes(payload)
    (ROOT/'SHA256SUMS.txt').write_text(sha(payload)+'  dist/'+target.name+'\n',encoding='utf-8')
    (ROOT/'INTEGRITY.json').write_bytes(jbytes({k:sha(v) for k,v in sorted(files.items())}))
    return target,payload,files
if __name__=='__main__':
    p,payload,files=build(); print(json.dumps({'zip':str(p),'bytes':len(payload),'sha256':sha(payload),'members':len(files)},ensure_ascii=False))

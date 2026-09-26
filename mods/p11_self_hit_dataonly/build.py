"""Package the explicitly requested experimental data-only addon; never deploy it."""
import hashlib
import io
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from resource_archive import make_archive, lua_resources

def lua(value):
    if value is True: return 'true'
    if value is False: return 'false'
    if value is None: return 'nil'
    if isinstance(value,str): return json.dumps(value,ensure_ascii=True)
    if isinstance(value,(int,float)): return str(value)
    if isinstance(value,list): return '{'+','.join(map(lua,value))+'}'
    if isinstance(value,dict): return '{'+','.join('['+lua(k)+']='+lua(v) for k,v in sorted(value.items()))+'}'
    raise TypeError(type(value))

def bundle():
    p=json.loads((HERE/'profile.json').read_bytes())
    baseline=json.loads((ROOT/'patches/25480438/manifest.json').read_bytes())
    assert p['game_sha256']==baseline['target']['game_dll_sha256'].lower()
    assert p['exe_sha256']==baseline['target']['executable_sha256'].lower()
    assert p['gameplay_verified'] is False and p['pre_collision_timing_verified'] is False
    assert p['loaded_section_indices']==[1,2,3,4]
    checked=[p['sections'][i-1] for i in p['loaded_section_indices']]
    module_rvas=[0x3326468,0x346bf98,0x33266d8,0x3326dc0,0x347cea8,0x37c7670+318*8]
    for rva in module_rvas+[a['rva'] for a in p['code_anchors']]:
        assert any(s['rva']<=rva and rva+8<=s['rva']+s['virtual_size'] for s in checked), 'Used RVA outside validated original sections'
    text='-- HD2-Addon: '+p['resource']+'\n-- DATA-ONLY EXPERIMENTAL; native healing is unverified.\n'
    for name,file in [('Core','core.lua'),('Version','version.lua'),('MakeImage','image_windows.lua'),('MakeData','data_windows.lua'),('Entry','entry.lua')]:
        text+='local '+name+'=(function()\n'+(HERE/file).read_text(encoding='utf-8')+'\nend)()\n'
    text+='return Entry(Core,Version,MakeImage,MakeData,'+lua(p)+',_G)\n'
    for forbidden in ('VirtualProtect','VirtualAlloc','FlushInstructionCache','CreateRemoteThread','OpenProcess','P11OBS','P11CAP02','GetAsyncKeyState'):
        assert forbidden not in text, 'Unexpected capability: '+forbidden
    assert text.count('kernel.WriteProcessMemory(process,ptr(at),desired,2,got)')==1
    return text.encode('utf-8'),p

def build():
    # Avoid the other tools/build.py module name; ZIP construction is deterministic.
    import zipfile
    source,p=bundle()
    archive=make_archive(p['resource'],source)
    parsed,=lua_resources(io.BytesIO(archive),len(archive))
    assert parsed['body']==source and parsed['declaration']==p['resource']
    manifest={'Version':1,'Guid':p['manager_guid'],'Name':'P-11 Self-Hit Data Only 0.2.1 - EXPERIMENTAL',
        'Description':'Build 25480438; Shared Loader API1/internal16. Clears runtime 0x20 on eligible own P-11 darts. No native hook. Healing and update timing unverified.',
        'Options':[{'Name':'Enable experimental P-11 self-hit data change','Description':'Arsenal controls this independent addon. Original homing remains unchanged.','Include':['Addon']}]}
    files={'manifest.json':(json.dumps(manifest,indent=2)+'\n').encode(),
        'Addon/9ba626afa44a3aa3.patch_0':archive,'Addon/9ba626afa44a3aa3.patch_0.stream':b'',
        'Addon/9ba626afa44a3aa3.patch_0.gpu_resources':b'', 'README.md':(HERE/'README-zh-TW.md').read_bytes(),
        'Source/p11_self_hit_dataonly.lua':source,'Source/profile.json':(HERE/'profile.json').read_bytes(),
        'Source/VALIDATION.md':(HERE/'VALIDATION.md').read_bytes()}
    target=ROOT/'dist/P11-Self-Hit-DataOnly-0.2.1-build25480438.zip'; target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):
            item=zipfile.ZipInfo(name,(2026,9,26,0,0,0)); item.compress_type=zipfile.ZIP_DEFLATED; item.external_attr=0o100644<<16
            z.writestr(item,data)
    with zipfile.ZipFile(target) as z: assert z.testzip() is None
    report={'package':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'lua_sha256':hashlib.sha256(source).hexdigest(),'lua_bytes':len(source),
        'core_lines':len((HERE/'core.lua').read_text().splitlines()),'resource':p['resource'],'manager_guid':p['manager_guid'],
        'data_writer_implemented':True,'native_hook':False,'executable_memory_writes':False,
        'self_heal_verified':False,'pre_collision_timing_verified':False,'slot_generation_verified':False,
        'runtime_tested':False,'original_homing_modified':False,'deployed':False,
        'fix':'0.2.0 startup rejection: separate disk and virtual layout checks; bounded deferred activation, no writes until all gates pass'}
    (ROOT/'dist/SELF-HIT-DATAONLY-BUILD.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__': build()

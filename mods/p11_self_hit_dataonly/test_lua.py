"""Run isolated LuaJIT mock tests; never execute the complete native addon."""
import argparse
import json
from pathlib import Path
import sys
import struct
HERE=Path(__file__).resolve().parent

def run(deps=None,capture_dir=None):
    if deps: sys.path.insert(0,str(deps.resolve()))
    from lupa.luajit21 import LuaRuntime
    from build import bundle,lua
    results={}
    for name,modules in [('core',{'Core':'core.lua','Fixture':'test_fixture.lua'}),
                         ('data_windows',{'Core':'core.lua','Fixture':'test_fixture.lua','MakeData':'data_windows.lua'}),
                         ('entry',{'Entry':'entry.lua'})]:
        runtime=LuaRuntime(encoding=None,unpack_returned_tuples=True)
        for key,file in modules.items(): runtime.globals()[key.encode()]=runtime.execute((HERE/file).read_bytes())
        runtime.globals()[b'Profile']=runtime.eval(lua(json.loads((HERE/'profile.json').read_bytes())).encode())
        results[name]=runtime.execute((HERE/('test_'+name+'.lua')).read_bytes())
    p=json.loads((HERE/'profile.json').read_bytes())
    anchors={a['rva']:bytes.fromhex(a['bytes_hex']) for a in p['code_anchors']}
    if capture_dir:
        sys.path.insert(0,str(capture_dir.resolve()))
        from capture_image import Image
        image=Image(capture_dir)
        assert image.report['capture_sha256']=='5888cbfe7abe46965b752715414b550a8d09bed968c0c55109a22c30cdbeb4d8'
        for a in p['code_anchors']:
            expected=bytes.fromhex(a['bytes_hex'])
            assert image.read(a['rva'],len(expected))==expected,a['name']
            anchors[a['rva']]=expected
        header=image.read(0,4096)
    else:
        # Synthetic schema fixture: tests guard behavior, not a game's layout.
        header=bytearray(4096); pe=p['pe_offset']; opt=pe+24
        header[:2]=b'MZ'; struct.pack_into('<I',header,0x3c,pe); header[pe:pe+4]=b'PE\0\0'
        struct.pack_into('<HHI',header,pe+4,0x8664,p['section_count'],p['timestamp'])
        struct.pack_into('<H',header,pe+20,p['optional_size'])
        struct.pack_into('<H',header,opt,0x20b); struct.pack_into('<I',header,opt+32,4096)
        struct.pack_into('<I',header,opt+56,p['image_size'])
        for i,s in enumerate(p['sections']):
            at=opt+p['optional_size']+i*40
            for off,key in [(8,'virtual_size'),(12,'rva'),(16,'raw_size'),(20,'raw_offset'),(36,'characteristics')]:
                struct.pack_into('<I',header,at+off,s[key])
        header=bytes(header)
    runtime=LuaRuntime(encoding=None,unpack_returned_tuples=True)
    runtime.globals()[b'Version']=runtime.execute((HERE/'version.lua').read_bytes())
    runtime.globals()[b'Profile']=runtime.eval(lua(p).encode())
    runtime.globals()[b'Header']=header
    runtime.globals()[b'AnchorFixture']=runtime.table_from(anchors)
    results['version']=runtime.execute((HERE/'test_version.lua').read_bytes())
    runtime=LuaRuntime(encoding=None)
    source,p=bundle()
    assert runtime.eval(b'function(s) return assert(loadstring(s)) end')(source) is not None
    report={'mock_assertions':results,'total':sum(results.values()),'version_fixture':'private captured image' if capture_dir else 'synthetic profile schema', 'bundle_compiled_only':True,'native_execution':False}
    print(json.dumps(report,indent=2)); return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--deps',type=Path)
    parser.add_argument('--capture-dir',type=Path)
    args=parser.parse_args(); run(args.deps,args.capture_dir)

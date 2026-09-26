"""Deterministic mod/source packaging plus a Windows portable diagnostic build."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile
from build_self_hit_release import NAME as SELF_NAME, EXPECTED as SELF_HASH, export_source, zip_files
from build_selectable_mod import VERSION, NAME as SELECTABLE_NAME, CHOICES, build_selectable
from maintenance import TOOLKIT_VERSION

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist/release'
TOOLS = ('collect_build_info.py', 'compatibility_report.py', 'resource_archive.py',
         'offline_locator.py', 'offline_update.py', 'log_parser.py', 'maintenance.py', 'portable_entry.py')
TOOLKIT_NAME = f'P11-Enhanced-Update-Toolkit-{TOOLKIT_VERSION}-win-x64.zip'

def sha(data): return hashlib.sha256(data).hexdigest()
def json_bytes(value): return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')

def source_files():
    allow=json.loads((ROOT/'publication-files.json').read_bytes())
    paths=[ROOT/n for n in allow['files']]
    for folder,suffixes in allow['folders'].items():
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts)
    files={p.relative_to(ROOT).as_posix():p.read_bytes() for p in sorted(set(paths))}
    for source,destination in allow['document_exports'].items(): files[destination]=(ROOT/source).read_bytes()
    return files

def build_mods():
    (ROOT/'dist').mkdir(parents=True,exist_ok=True)
    original=ROOT/'dist'/SELF_NAME
    if not original.exists():
        subprocess.run([sys.executable,str(ROOT/'mods/p11_self_hit_dataonly/build.py')],check=True)
    if sha(original.read_bytes())!=SELF_HASH:
        raise ValueError('Refusing to replace the tested P-11 package with different bytes')
    spec=importlib.util.spec_from_file_location('weapon_candidate_builder',ROOT/'mods/weapon_self_hit_candidate/build.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    baseline_path=ROOT/'maintenance/baselines.json'
    baselines=json.loads(baseline_path.read_bytes())
    components=baselines['baselines'][0]['components']
    packages={SELF_NAME:original.read_bytes()}
    for scope,feature in [('pistols','pistol_self_hit'),('native_no_shotguns','native_no_shotgun_self_hit'),('native_weapons','native_weapon_self_hit')]:
        result=builder.build(scope);p=Path(result['path']);source,profile=builder.bundle(scope)
        packages[p.name]=p.read_bytes()
        components[feature]={'package':p.name,'package_sha256':sha(p.read_bytes()),'lua_sha256':sha(source),
            'resource':profile['resource'],'scope':scope,'version':profile['version'],'user_confirmed_basic_behavior':False,
            'verification_scope':'Offline source/guard and Lua mock checks only; native self-hit or damage, current pistol IDs and broad mechanism coverage have no gameplay confirmation.'}
    baseline_path.write_bytes(json_bytes(baselines))
    name, data = build_selectable(packages)
    packages[name] = data
    return packages

def portable_sources(): return {n:sha((ROOT/'tools'/n).read_bytes()) for n in TOOLS}

def build_portable(reuse=False):
    if sys.platform!='win32': raise ValueError('Build the portable EXE on Windows x64')
    out=ROOT/'build/portable';out.mkdir(parents=True,exist_ok=True)
    stamp=out/'source-hashes.json';exe=out/'P11-Update.exe'
    if reuse:
        record=json.loads(stamp.read_bytes())
        if record['sources']!=portable_sources() or record['exe_sha256']!=sha(exe.read_bytes()):
            raise ValueError('Portable EXE differs from these sources; rebuild without --reuse-portable')
    else:
        subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--console',
            '--noupx','--name','P11-Update','--distpath',str(out),'--workpath',str(ROOT/'build/pyinstaller'),
            '--specpath',str(ROOT/'build'),'--paths',str(ROOT/'tools'),str(ROOT/'tools/portable_entry.py')],check=True)
        stamp.write_bytes(json_bytes({'sources':portable_sources(),'exe_sha256':sha(exe.read_bytes())}))
    for attempt in range(6):
        try:
            result=subprocess.run([str(exe),'--help'],capture_output=True,check=True);break
        except PermissionError:
            if attempt==5: raise
            time.sleep(1)
    if b'--game' not in result.stdout: raise ValueError('Portable help verification failed')
    return exe

def runtime_licenses():
    files={}
    for root in (Path(sys.base_prefix),Path(sys.base_prefix)/'Lib'):
        p=root/'LICENSE.txt'
        if p.is_file():files['runtime-licenses/Python-LICENSE.txt']=p.read_bytes();break
    dist=importlib.metadata.distribution('pyinstaller')
    for p in dist.files or []:
        if Path(str(p)).name=='COPYING.txt':
            files['runtime-licenses/PyInstaller-COPYING.txt']=Path(dist.locate_file(p)).read_bytes();break
    if len(files)!=2:raise ValueError('Missing bundled runtime license')
    return files

def toolkit_files(sources, exe, packages, licenses):
    """Explicit public inputs only; the toolkit is not an installable mod."""
    files = {
        'P11-Update.exe': exe,
        'Collect-HD2-Update.cmd': sources['Collect-HD2-Update.cmd'],
        'README.md': sources['docs/COLLECTION.md'],
        'LICENSE-NOTICE.md': sources['LICENSE-NOTICE.md'],
        'AGENTS.md': ('# P11-Enhanced 維護工具包\n\n'
                      '先閱讀 README.md，再進入 Source/P11-Enhanced/。\n'
                      '開發與修補必須先讀 Source/P11-Enhanced/AGENTS.md，'
                      '依 Source/P11-Enhanced/docs/AGENT_GUIDE.md 操作。\n'
                      '本目錄只執行離線收集；建置命令從源碼目錄執行。\n'
                      'diagnostics/ 是私人證據，不屬於源碼或發布內容。\n').encode('utf-8'),
        'MOD-SHA256SUMS.txt': ''.join(sha(d)+'  '+n+'\n' for n,d in sorted(packages.items())).encode('ascii'),
    }
    files.update({'tools/'+n:sources['tools/'+n] for n in TOOLS})
    files.update({n:d for n,d in sources.items() if n.startswith(('maintenance/','patches/'))})
    files.update({'Source/P11-Enhanced/'+n:d for n,d in sources.items()})
    files.update(licenses)
    return files


def public_asset_names():
    return [SELECTABLE_NAME, *(choice[1] for choice in CHOICES), TOOLKIT_NAME]

def build(reuse=False):
    packages=build_mods()
    exe=build_portable(reuse)
    files=source_files();export_source(files)
    DIST.mkdir(parents=True,exist_ok=True)
    for n,d in packages.items():(DIST/n).write_bytes(d)
    toolkit=toolkit_files(files,exe.read_bytes(),packages,runtime_licenses())
    zip_files(DIST/TOOLKIT_NAME,toolkit)
    names=public_asset_names()
    (DIST/'SHA256SUMS.txt').write_bytes(''.join(sha((DIST/n).read_bytes())+'  '+n+'\n' for n in names).encode('ascii'))
    # The checksum file is local-only; the publisher includes its table in release notes.
    report={'project':'P11-Enhanced','release':VERSION,'prerelease':True,'public_assets':names,
            'published':False,'self_hit_original_preserved':True,'expanded_scopes_gameplay_verified':False,
            'source_manifest':{n:sha(d) for n,d in files.items()},
            'assets':{n:{'sha256':sha((DIST/n).read_bytes()),'bytes':(DIST/n).stat().st_size} for n in names}}
    (DIST/'PUBLIC-ASSETS.json').write_bytes(json_bytes(report))
    print(json.dumps({k:v for k,v in report.items() if k!='source_manifest'},indent=2))
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mods-only',action='store_true',help='Rebuild the selectable mod and its four standalone inputs using only Python standard library')
    parser.add_argument('--reuse-portable',action='store_true',help='Reuse only an EXE with matching recorded source hashes')
    args=parser.parse_args()
    if args.mods_only: print(json.dumps({n:sha(d) for n,d in build_mods().items()},indent=2))
    else:build(args.reuse_portable)

if __name__=='__main__': main()

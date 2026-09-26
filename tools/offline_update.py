"""One-run offline evidence collection. No network, process access, or deployment."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile
from collect_build_info import collect_build_info
from compatibility_report import compare_manifest, load_manifest
from log_parser import parse_log
from resource_archive import inspect_file, resource_hash
from offline_locator import scan
from maintenance import assess, load_metadata, write_handoff

ROOT=Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[1]
PACKAGE_WORDS=re.compile(r'bingus.*loader|homing[ _-]?stim|p11.*(?:homing|self|enhanced)|stim.*self|weapon[ _-]self[ _-]hit',re.I)
LOG_WORDS=re.compile(r'^(?:BingusSharedLoader|StimHoming.*|HealingPistolEnhanced|P11StimSelfHit|StimSelfHit.*|P11ReadOnlyCapture|P11OwnedProjectileObserver|WeaponSelfHitCandidate)\.log$',re.I)
SCHEMA_NAMES={'projectile_settings.json','generated_projectile_settings.json','generated_projectile_settings.dl_bin','projectile_settings.go','weapon_settings.go'}

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def signature(path):
    p=Path(path)
    try:
        s=p.stat(); return [s.st_size,s.st_mtime_ns]
    except OSError: return None

def write_json(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def discover_games(extra=()):
    candidates=[Path(x) for x in extra if x]
    if os.environ.get('HD2_GAME_ROOT'): candidates.append(Path(os.environ['HD2_GAME_ROOT']))
    steam=[]
    if sys.platform=='win32':
        import winreg
        for hive,key in [(winreg.HKEY_CURRENT_USER,r'Software\Valve\Steam'),(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\WOW6432Node\Valve\Steam')]:
            try:
                with winreg.OpenKey(hive,key) as k:
                    for name in ('SteamPath','InstallPath'):
                        try: steam.append(Path(winreg.QueryValueEx(k,name)[0]))
                        except OSError: pass
            except OSError: pass
    for key in ('ProgramFiles(x86)','ProgramFiles'):
        if os.environ.get(key): steam.append(Path(os.environ[key])/'Steam')
    # Bounded common locations; never recursively search disks.
    for drive in 'CDEFGHIJKLMNOP':
        for tail in ('Steam','Game/Steam','Games/Steam','SteamLibrary'):
            steam.append(Path(f'{drive}:/')/tail)
    for library in list(steam):
        vdf=library/'steamapps/libraryfolders.vdf'
        try:
            if vdf.stat().st_size<1024*1024:
                for p in re.findall(r'"path"\s*"([^"\r\n]+)"',vdf.read_text(encoding='utf-8-sig')):
                    steam.append(Path(p.replace('\\\\','\\')))
        except OSError: pass
    candidates.extend(p/'steamapps/common/Helldivers 2' for p in steam)
    result=[]
    for p in candidates:
        if (p/'bin/helldivers2.exe').is_file() and (p/'data/game/game.dll').is_file():
            resolved=p.resolve()
            if resolved not in result: result.append(resolved)
    return result

def steam_state(game):
    path=game.parent.parent/'appmanifest_553850.acf'
    if not path.is_file(): return {'present':False}
    text=path.read_text(encoding='utf-8-sig')
    result={'present':True}
    # Whitelist fields. Do not retain LastOwner, UserConfig, or raw manifest.
    for key in ('StateFlags','buildid','TargetBuildID','BytesToDownload','BytesDownloaded','BytesToStage','BytesStaged'):
        match=re.search(r'"'+key+r'"\s*"(\d+)"',text,re.I)
        if match: result[key]=int(match[1])
    result['update_in_progress']=result.get('StateFlags')!=4
    return result

def classify_resource(body,declaration,resource_id=None):
    if declaration == 'mods/p11/self_hit_dataonly': return ['p11_addon','self_hit']
    if declaration == 'mods/weapon_self_hit/pistols': return ['p11_addon','pistol_self_hit']
    if declaration == 'mods/weapon_self_hit/native_no_shotguns': return ['p11_addon','native_no_shotgun_self_hit']
    if declaration == 'mods/weapon_self_hit/native_weapons': return ['p11_addon','native_weapon_self_hit']
    # Research source contains conflict-marker names, not those gameplay writers.
    if declaration in ('mods/p11_research/code_capture_25480438',
                       'mods/p11_research/owned_projectile_observer_25480438'): return ['p11_addon','research_capture']
    names=[]
    text_loader=b'CowboyBingusModLoader' in body and b'state.open_log' in body
    bytecode_loader=(resource_id=='7251fdd9bb62480a' and body.startswith(b'\x1bLJ')
                     and all(s in body for s in (b'CowboyBingusModLoader',b'open_log',b'Bingus Shared Loader loader-v')))
    if text_loader or bytecode_loader: names.append('loader')
    if declaration and re.search(r'stim|p11|healing',declaration,re.I): names.append('p11_addon')
    if b'StimHomingAcquisitionTest' in body: names.append('homing')
    if any(x in body for x in (b'StimSelfHitExperimental01',b'StimSelfHitDataOnly01',b'P11StimSelfHitDataOnly11')): names.append('self_hit')
    if b'HealingPistolEnhanced' in body: names.append('integrated')
    return names

def collect_deployed(game,folder,watched):
    records=[]; all_lua=[]; errors=[]
    pins_file=ROOT/'maintenance/loader-profiles.json'
    pins=json.loads(pins_file.read_bytes())['profiles'] if pins_file.is_file() else []
    archives=sorted((game/'data').glob('9ba626afa44a3aa3.patch_*'),key=lambda p:int(p.name.rsplit('_',1)[-1]) if p.name.rsplit('_',1)[-1].isdigit() else -1)
    for path in archives:
        if not path.name.rsplit('_',1)[-1].isdigit(): continue
        watched[path]=signature(path)
        try:
            for item in inspect_file(path):
                body=item.pop('body'); roles=classify_resource(body,item['declaration'],item['resource_hash'])
                row={**item,'archive':path.name,'patch_index':int(path.name.rsplit('_',1)[-1]),'sha256':hashlib.sha256(body).hexdigest(),'size_bytes':len(body),'roles':roles}
                if roles:
                    text=body.decode('utf-8',errors='replace')
                    row['plaintext']=not body.startswith(b'\x1b')
                    if 'loader' in roles:
                        version=re.search(r'state\s*=\s*\{\s*version\s*=\s*(\d+)\s*,\s*api\s*=\s*(\d+)',text)
                        if version: row.update(internal_version=int(version[1]),api=int(version[2]))
                        row['public_release']='unknown: requires exact release provenance'
                        banner=re.search(rb'Bingus Shared Loader loader-(v[0-9]+); API ([0-9]+)',body)
                        if banner:
                            row['embedded_version_label']={'public_release':banner[1].decode(),'api':int(banner[2])}
                            row.setdefault('api',int(banner[2]))
                        pin=next((p for p in pins if p['lua_sha256']==row['sha256'] and p['resource_hash']==row['resource_hash']),None)
                        if pin:
                            row.update({k:pin[k] for k in ('public_release','internal_version','api')})
                            row['version_evidence']='exact known loader resource SHA256; declared API/internal version from author source'
                    row['uses_code_patch_api']=b'VirtualProtect' in body or b'FlushInstructionCache' in body
                    target=folder/'deployed'/f'{path.name}-{row["resource_hash"]}.lua-resource'
                    target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(body)
                    records.append(row)
                all_lua.append(row)
        except (OSError,ValueError) as exc: errors.append({'archive':path.name,'error':str(exc)})
    winners={}
    for row in all_lua: winners[row['resource_hash']]=row
    for row in records: row['winning_resource']=winners.get(row['resource_hash']) is row
    active=[r for r in records if r['winning_resource']]
    loader=[r for r in active if 'loader' in r['roles']]
    gameplay=[r for r in active if set(r['roles']) & {'homing','self_hit','integrated','pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit'}]
    duplicates=[role for role in ('self_hit','homing','integrated','pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit') if sum(role in r['roles'] for r in gameplay)>1]
    scope_conflict=sum(any(role in r['roles'] for r in gameplay) for role in ('pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit'))>1
    combined_legacy=any('integrated' in r['roles'] for r in gameplay) and len(gameplay)>1
    return {'resources':records,'archive_errors':errors,'loader_observed':bool(loader),
            'possible_gameplay_conflict':bool(duplicates or combined_legacy or scope_conflict),'duplicate_roles':duplicates,
            'mutually_exclusive_scopes_present':scope_conflict,
            'two_independent_addons_present':any('self_hit' in r['roles'] for r in gameplay) and any('homing' in r['roles'] for r in gameplay),
            'active_gameplay_resources':[r['resource_hash'] for r in gameplay],'scope':'deployed resources only; installed does not prove loaded or working'}

def safe_copy(source,target,watched,expected=None):
    source=Path(source); watched.setdefault(source,signature(source))
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target); copied=digest(target)
    if expected and copied.lower()!=expected.lower(): raise ValueError('binary changed between inspection and copying')
    if signature(source)!=watched[source]: raise ValueError('file changed during copy')
    return {'file':target.name,'sha256':copied,'size_bytes':target.stat().st_size}

def changes_from(previous,current):
    if not previous: return {'baseline_available':False,'verified_baseline':False,'changes':[]}
    changes=[]
    for key in ('executable','game_dll'):
        before=previous.get('build',{}).get('files',{}).get(key,{}).get('sha256')
        after=current['build']['files'].get(key,{}).get('sha256')
        if before!=after: changes.append({'item':key,'affected_features':['self_heal','pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit']})
    def resources(report):
        return {r['resource_hash']:r['sha256'] for r in report.get('deployed',{}).get('resources',[]) if r.get('winning_resource')}
    if resources(previous)!=resources(current): changes.append({'item':'deployed_resources','affected_features':['addon_loading','self_heal','pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit']})
    # Collections alone can never be promoted to verified baselines.
    return {'baseline_available':True,'verified_baseline':False,'changes':changes}

def snapshot(game,output,packages=(),schema_dirs=(),logs=None,previous=None,profiles=None):
    game=Path(game).resolve(); output=Path(output).resolve()
    if output.is_relative_to(game): raise ValueError('output must be outside the game directory')
    output.mkdir(parents=True,exist_ok=False)
    watched={}; errors=[]
    initial_archive_names=sorted(p.name for p in (game/'data').glob('9ba626afa44a3aa3.patch_*'))
    manifest=game.parent.parent/'appmanifest_553850.acf'; watched[manifest]=signature(manifest)
    state=steam_state(game)
    for rel in ('bin/helldivers2.exe','data/game/game.dll'): watched[game/rel]=signature(game/rel)
    build=collect_build_info(game)
    report={'schema_version':1,'collected_utc':datetime.now(timezone.utc).isoformat(),'build':build,'steam_state':state,'runtime_verified':False,'complete':False,'errors':errors,'packages':[],'schema_sources':[],'log_reports':[]}
    for key,rel in [('executable','bin/helldivers2.exe'),('game_dll','data/game/game.dll')]:
        try:
            if not build['files'][key].get('sha256'): raise ValueError('required binary missing or unreadable')
            safe_copy(game/rel,output/'binaries'/Path(rel).name,watched,build['files'][key]['sha256'])
        except (OSError,ValueError) as exc: errors.append({'item':key,'error':str(exc)})
    report['deployed']=collect_deployed(game,output,watched)
    errors.extend({'item':e['archive'],'error':e['error']} for e in report['deployed']['archive_errors'])
    seen=set()
    for path in packages:
        path=Path(path).resolve()
        if path in seen: continue
        seen.add(path)
        try:
            if not zipfile.is_zipfile(path) or path.stat().st_size>256*1024*1024: raise ValueError('unsupported or oversized package')
            with zipfile.ZipFile(path) as z:
                if len(z.infolist())>10000: raise ValueError('too many package entries')
                names=z.namelist(); manifests=[n for n in names if n.lower()=='manifest.json']
                metadata={}
                if manifests:
                    entry=z.getinfo(manifests[0])
                    if entry.file_size>1024*1024: raise ValueError('oversized manager manifest')
                    manager=json.loads(z.read(entry))
                    metadata={k:manager[k] for k in ('Guid','Name','Version') if k in manager}
                info=safe_copy(path,output/'packages'/path.name,watched)
                report['packages'].append({**info,'manager':metadata,'source':'local package, not evidence of deployment','entry_count':len(names)})
        except (OSError,ValueError,zipfile.BadZipFile) as exc: errors.append({'item':path.name,'error':str(exc)})
    for directory in schema_dirs:
        directory=Path(directory)
        for name in sorted(SCHEMA_NAMES):
            p=directory/name
            if not p.is_file(): continue
            try:
                if p.stat().st_size>64*1024*1024: raise ValueError('schema/data file exceeds collection limit')
                h=digest(p); target=output/'schemas'/h[:12]/name
                info=safe_copy(p,target,watched)
                report['schema_sources'].append({**info,'evidence_file':target.relative_to(output).as_posix(),'matches_game_build':False,'provenance':'local cached file; game-version correspondence unproven'})
            except (OSError,ValueError) as exc: errors.append({'item':name,'error':str(exc)})
    if logs and Path(logs).is_dir():
        for p in sorted(Path(logs).glob('*.log')):
            if not LOG_WORDS.match(p.name): continue
            try:
                watched[p]=signature(p)
                if p.stat().st_size>8*1024*1024: raise ValueError('log exceeds collection limit')
                item={'file':p.name,'mtime_utc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'sha256':digest(p),'triage':parse_log(p.read_text(encoding='utf-8-sig',errors='replace')),'proves_current_build':False}
                report['log_reports'].append(item)
            except (OSError,ValueError) as exc: errors.append({'item':p.name,'error':str(exc)})
    report['profiles']=[]
    for p in sorted((ROOT/'patches').glob('*/manifest.json')) if profiles is None else profiles:
        try:
            profile=load_manifest(p)
            item={'comparison':compare_manifest(build,profile),'profile':profile,'offline_candidates':[]}
            dll=output/'binaries/game.dll'
            if dll.is_file():item['offline_candidates']=scan(dll,build['files']['game_dll'].get('pe',{}),profile.get('locators',[]))
            report['profiles'].append(item)
        except (OSError,ValueError) as exc: errors.append({'item':'profile','error':str(exc)})
    report['previous_collection_comparison']=changes_from(previous,report)
    for p,before in watched.items():
        if signature(p)!=before: errors.append({'item':p.name,'error':'source changed or disappeared during collection'})
    if initial_archive_names!=sorted(p.name for p in (game/'data').glob('9ba626afa44a3aa3.patch_*')):
        errors.append({'item':'deployed_archives','error':'deployment changed during collection'})
    if state.get('update_in_progress'): errors.append({'item':'steam','error':'Steam reports a non-idle installation/update state'})
    report['gaps']=['Offline data and old logs do not verify current native hit/heal, host/client behavior, or candidate weapon coverage / coexistence. P-11 reports do not validate either broader candidate.']
    if not report['deployed']['loader_observed']: report['gaps'].append('No identifiable active loader resource found; loader deployment needs inspection.')
    if not report['schema_sources']: report['gaps'].append('No local projectile schema/data cache was available.')
    report['complete']=not errors and all(x.get('sha256') and not x.get('pe_error') for x in build['files'].values())
    baselines,porting_map=load_metadata(ROOT)
    report['feature_assessment']=assess(report,baselines)
    if any(f['required_p11_missing'] for f in report['feature_assessment']):
        report['gaps'].append('An expanded scope is deployed without the required included P-11 resource. It may be an older standalone candidate or incomplete deployment; use one new complete variant in Arsenal.')
    write_handoff(output,report,porting_map)
    # complete means stable collection only, never complete/working gameplay.
    write_json(output/'report.json',report)
    summary=['# P11-Enhanced 離線更新診斷','',f"遊戲構建：{build['game']['steam_build_id'] or '未知'}",f"收集狀態：{'完成（檔案穩定）' if report['complete'] else '不完整，請查看錯誤'}",'','本報告沒有啟動遊戲、修改模組、讀取程序或上傳資料。','離線收集完成不代表本次自療、自命中或傷害已驗證。','',f"可辨識 loader：{'有' if report['deployed']['loader_observed'] else '未找到'}",f"可能有重複玩法模組：{'是，檢查重複來源' if report['deployed']['possible_gameplay_conflict'] else '未觀察到'}",'','## 功能結果']
    for f in report['feature_assessment']:
        summary += [f"- **{f['name']}：{f['label']}**",f"  - 部署：`{f['deployment']}`；loader：`{f['loader']}`。",f"  - 已有證據範圍：{f['recorded_scope']}"]
    summary += ['','`matches_package` 表示部署 Lua 與記錄相同；`not_deployed` 表示未發現；',
                '`different_or_unidentified_source` 表示需檢查套件，`incompatible` 表示 loader API／版本不符合。',
                '「符合基準」只比較遊戲身份與已有玩法回報，仍須同時查看部署與 loader 欄。','','## 定位候選']
    for item in report['profiles']:
        c=item['comparison']; summary.append(f"- {c['patch_id']}: {c['status']}")
        for candidate in item['offline_candidates']:
            summary.append(f"  - {candidate['id']}: {candidate['status']}；候選 {len(candidate['candidates'])} 個，不能據此啟用功能。")
    summary+=['','## 接下來','- 0.2.1 已有基本自命中治療的使用者確認；未知遊戲 build 不沿用此確認。','- 在 Arsenal 的四選一模組中選一個範圍，全部內建 P-11；停用舊獨立包。任兩個擴展方案同時部署時必須先排除衝突。','- 維修時提供本診斷 ZIP 與公開 Source ZIP；維修要求已寫入「維修交接.md」。','- 找到候選位置也不會自動改雜湊、生成已驗證補丁或部署。','','## 仍缺少的證據','- 未知版本需要重新確認資料布局、所有權及碰撞時機。','- 手槍白名單、武器機制覆蓋、主／客機、切槍、死亡及候選與 P-11 共存的玩法證據。','- 舊日誌及本機資料快取的版本不能自動視為本次遊戲版本。','',f"與上次收集比較：{len(report['previous_collection_comparison']['changes'])} 項變更；上次收集不等於已驗證版本。",'','詳細檔案、來源雜湊、受影響功能與錯誤請查看 report.json。','請只在私人本機分析使用 binaries/packages，勿放入公開原始碼倉庫。']
    if report['deployed']['mutually_exclusive_scopes_present']:
        summary += ['', '## 互斥版本衝突', '多個擴展候選同時存在，執行時會停止。關閉遊戲後在 Arsenal 四選一並重新部署。']
    if any(f['required_p11_missing'] for f in report['feature_assessment']):
        summary += ['', '## 缺少內建 P-11 自療資源', '已發現擴展候選，卻未辨識到 P-11 自療資源；可能是舊獨立候選包或部署不完整。新的四個方案均內建 P-11。關閉遊戲後在 Arsenal 停用舊版、選擇一個完整新包並重新部署。工具沒有自動修復或部署。']
    if errors: summary+=['','## 收集錯誤']+[f"- {e['item']}: {e['error']}" for e in errors]
    (output/'摘要.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game',type=Path);parser.add_argument('--output',type=Path,default=ROOT/'diagnostics')
    parser.add_argument('--package',action='append',default=[],type=Path);parser.add_argument('--schema-dir',action='append',default=[],type=Path)
    parser.add_argument('--no-auto-packages',action='store_true');parser.add_argument('--logs',type=Path)
    args=parser.parse_args()
    print('P11-Enhanced：正在收集離線版本、模組及既有日誌，請等待。',flush=True)
    local={}; settings=ROOT/'local-settings.json'
    if settings.is_file(): local=json.loads(settings.read_text(encoding='utf-8-sig'))
    found=discover_games([args.game] if args.game else [local.get('game_root')])
    if args.game and args.game.resolve() not in found: parser.error('specified game directory lacks required files')
    if args.game: game=args.game.resolve()
    elif len(found)==1: game=found[0]
    elif found and sys.stdin.isatty():
        for i,p in enumerate(found,1): print(f'{i}. {p}')
        game=found[int(input('Select installation number: '))-1]
    elif not found and sys.stdin.isatty():
        game=Path(input('Helldivers 2 folder: ').strip().strip('"')).resolve()
        if game not in discover_games([game]): parser.error('required game files not found')
    else: parser.error('multiple/no installations: specify --game')
    out=args.output.resolve()
    if out.is_relative_to(game): parser.error('diagnostics output must be outside game directory')
    out.mkdir(parents=True,exist_ok=True)
    previous=None
    reports=sorted(out.glob('*/report.json'),key=lambda p:p.stat().st_mtime,reverse=True)
    if reports:
        try: previous=json.loads(reports[0].read_text(encoding='utf-8'))
        except (OSError,ValueError): pass
    packages=list(args.package)
    # The release collection stores the original installable ZIPs here.
    packages += sorted((ROOT/'Mods').glob('*.zip'))
    if not args.no_auto_packages:
        downloads=Path.home()/'Downloads'
        candidates=[p for p in downloads.glob('*.zip') if PACKAGE_WORDS.search(p.name)]
        packages+=sorted(candidates,key=lambda p:p.stat().st_mtime,reverse=True)[:12]
    schemas=list(args.schema_dir)+[Path(p) for p in local.get('schema_dirs',[])]+[ROOT/'reference-data']
    module_cache=Path(os.environ.get('GOMODCACHE',str(Path.home()/'go/pkg/mod')))
    schemas += [p/'datalibrary' for p in (module_cache/'github.com/xypwn').glob('filediver@*')][:20]
    logs=args.logs or Path(os.environ.get('LOCALAPPDATA',str(Path.home()))) / 'CowboyBingus/Helldivers2/Logs'
    name='HD2-Update-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    folder=out/name
    report=snapshot(game,folder,packages,schemas,logs,previous)
    archive=Path(shutil.make_archive(str(folder),'zip',root_dir=folder))
    write_json(out/'latest.json',{'folder':folder.name,'archive':archive.name,'sha256':digest(archive),'collection_complete':report['complete'],'runtime_verified':False})
    print('診斷包：',archive)
    print('收集完成（不代表功能已驗證）' if report['complete'] else '收集不完整：請查看摘要.md')
    return 0 if report['complete'] else 2

if __name__=='__main__':
    try: raise SystemExit(main())
    except (OSError,ValueError,IndexError) as exc: print(f'Collection failed: {exc}',file=sys.stderr);raise SystemExit(2)

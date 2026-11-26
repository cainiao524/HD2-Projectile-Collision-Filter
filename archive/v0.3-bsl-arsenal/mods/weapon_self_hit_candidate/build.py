"""Build three independent, unverified Arsenal candidate ZIPs; never deploy."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import uuid
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from resource_archive import make_lua_archive, lua_resources
from verify_secondary_catalog import load_catalog, runtime_hashes

BASE = json.loads((HERE.parent / 'p11_self_hit_dataonly' / 'profile.json').read_text(encoding='utf-8'))
# Frozen legacy metadata is retained in the two unchanged broad-scope ZIPs.
# The pistol scope below is generated from the separately reviewed catalog.
LEGACY_PISTOLS = {
    'P-2 Peacemaker': '05e4e5c2db6e44a2',
    'P-4 Senator': '8d3d52a3b2f19402',
    'P-19 Redeemer': '3575aabc5f1f9326',
    'P-69 Veto': 'c780bcd79547da0f',
    'P-92 Warrant': 'cf8934ff6567a42d',
    'P-113 Verdict': '1a437158e1b8d2a1',
    'P/40-K Bolt Pistol': 'dbb6c961c59fadc1',
    'M6C SOCOM Pistol': '4d58c77087b774c5',
}
SCOPES = {
    'pistols': ('Pistols No Shotguns Self-Hit Candidate', 'weapon_self_hit_pistols'),
    'native_no_shotguns': ('Native Weapons No Shotguns Self-Hit Candidate', 'weapon_self_hit_native_no_shotguns'),
    'native_weapons': ('All Native Weapon Projectiles Self-Hit Candidate', 'weapon_self_hit_native'),
}


def lua(v):
    if v is True: return 'true'
    if v is False: return 'false'
    if v is None: return 'nil'
    if isinstance(v, str): return json.dumps(v, ensure_ascii=True)
    if isinstance(v, (int, float)): return str(v)
    if isinstance(v, list): return '{' + ','.join(map(lua, v)) + '}'
    if isinstance(v, dict): return '{' + ','.join('[' + lua(k) + ']=' + lua(w) for k, w in sorted(v.items())) + '}'
    raise TypeError(type(v))


def profile(scope):
    assert scope in SCOPES
    p = dict(BASE)
    filters=json.loads((ROOT/'maintenance/projectile-exclusions-25480438.json').read_bytes())
    assert filters['target_build']=='25480438' and filters['p11_type']==318
    denied={r['type']:True for r in filters['excluded']}
    assert len(denied)==38 and 318 not in denied and filters['projectile_type_max']==350
    p.update(id='weapon-self-hit-candidate-0.1.2-25480438-' + scope,
             version='0.1.2-candidate', scope=scope,
             exclude_shotguns=scope!='native_weapons',
             excluded_projectile_types=denied if scope!='native_weapons' else {},
             projectile_type_max=filters['projectile_type_max'],
             projectile_filter_source_sha256=filters['table_source']['sha256'],
             resource='mods/weapon_self_hit/' + scope,
             manager_guid=str(uuid.uuid5(uuid.NAMESPACE_URL, 'P11-Enhanced/weapon-self-hit-candidate/' + scope)),
             pistol_unit_hashes=list(LEGACY_PISTOLS.values()),
             pistol_mapping_source='Offline mod archive index, 2026-09-01; not current-build gameplay proof',
             gameplay_verified=False, self_damage_verified=False)
    if scope == 'pistols':
        catalog = load_catalog()
        p.update(id='weapon-self-hit-candidate-0.1.3-25480438-pistols',
                 version='0.1.3-candidate',
                 pistol_unit_hashes=runtime_hashes(catalog),
                 pistol_mapping_source='Pinned Filediver LoadoutEntry SidearmWeapon + shooting components; reference classification only',
                 secondary_catalog_sha256=hashlib.sha256((ROOT/'maintenance/secondary-catalog-25480438.json').read_bytes()).hexdigest(),
                 all_secondary_mechanisms_supported=False)
    return p


def bundle(scope):
    p = profile(scope)
    baseline = json.loads((ROOT / 'patches/25480438/manifest.json').read_text(encoding='utf-8'))
    assert p['game_sha256'] == baseline['target']['game_dll_sha256'].lower()
    assert p['exe_sha256'] == baseline['target']['executable_sha256'].lower()
    assert p['loaded_section_indices'] == [1, 2, 3, 4]
    checked = [p['sections'][i - 1] for i in p['loaded_section_indices']]
    rvas = [0x3326468, 0x346bf98, 0x33266d8, 0x3326dc0, 0x347cea8, 0x37c7670 + 4096 * 8]
    for rva in rvas + [a['rva'] for a in p['code_anchors']]:
        assert any(s['rva'] <= rva and rva + 8 <= s['rva'] + s['virtual_size'] for s in checked)
    source = '-- HD2-Addon: ' + p['resource'] + '\n-- DATA-ONLY CANDIDATE; self-damage not verified.\n'
    for name, file in [('Core', 'core.lua'), ('Version', 'version.lua'), ('MakeImage', 'image_windows.lua'),
                       ('MakeData', 'data_windows.lua'), ('Entry', 'entry.lua')]:
        source += 'local ' + name + '=(function()\n' + (HERE / file).read_text(encoding='utf-8') + '\nend)()\n'
    source += 'return Entry(Core,Version,MakeImage,MakeData,' + lua(p) + ',_G)\n'
    for forbidden in ('VirtualProtect', 'VirtualAlloc', 'FlushInstructionCache', 'CreateRemoteThread',
                      'OpenProcess', 'GetAsyncKeyState'):
        assert forbidden not in source
    assert source.count('kernel.WriteProcessMemory(process,ptr(at),desired,2,got)') == 1
    return source.encode('utf-8'), p


def build(scope):
    source, p = bundle(scope)
    spec=importlib.util.spec_from_file_location('p11_preserved_builder',HERE.parent/'p11_self_hit_dataonly/build.py')
    original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
    p11_source,p11_profile=original.bundle()
    assert hashlib.sha256(p11_source).hexdigest()=='b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a'
    archive = make_lua_archive({p11_profile['resource']:p11_source,p['resource']:source})
    parsed={item['declaration']:item['body'] for item in lua_resources(io.BytesIO(archive),len(archive))}
    assert parsed=={p11_profile['resource']:p11_source,p['resource']:source}
    title, stem = SCOPES[scope]
    description = ('Build 25480438; Shared Loader API 1/internal 16. Experimental local native-projectile '
                   'source exclusion change, plus unchanged P-11 0.2.1 healing addon. '
                   'Expanded self-damage and coexistence unverified. Choose one of four variants. '
                   + ('Known shotgun/multishot types excluded before source lookup.' if p['exclude_shotguns'] else
                      'INCLUDES SHOTGUNS: additional per-pellet work can affect performance.'))
    if scope == 'pistols':
        title = 'Shootable Secondaries Native-Path Candidate'
        description += (' Sidearm catalog includes plasma and grenade weapons. Beam and spray systems are unsupported; '
                        'entity branches and gameplay remain unverified. This is not complete all-secondary support.')
    manifest = {'Version': 1, 'Guid': p['manager_guid'], 'Name': title,
                'Description': description,
                'Options': [{'Name': 'Enable ' + title,
                             'Description': 'Includes unchanged P-11 0.2.1. Install only one of the four self-hit variants.',
                             'Include': ['Addon']}]}
    files = {'manifest.json': (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode(),
             'Addon/9ba626afa44a3aa3.patch_0': archive,
             'Addon/9ba626afa44a3aa3.patch_0.stream': b'',
             'Addon/9ba626afa44a3aa3.patch_0.gpu_resources': b'',
             'README-zh-TW.md': (HERE / 'README-zh-TW.md').read_bytes(),
             'Source/weapon_self_hit_candidate.lua': source,
             'Source/p11_self_hit_dataonly.lua': p11_source,
             'Source/p11_profile.json': (json.dumps(p11_profile,ensure_ascii=False,indent=2)+'\n').encode(),
             'Source/profile.json': (json.dumps(p, ensure_ascii=False, indent=2) + '\n').encode(),
             'Source/projectile-exclusions.json': (ROOT/'maintenance/projectile-exclusions-25480438.json').read_bytes(),
             'Source/VALIDATION.md': (HERE / 'VALIDATION.md').read_bytes()}
    version = '0.1.3' if scope == 'pistols' else '0.1.2'
    if scope == 'pistols':
        files['Source/secondary-catalog.json'] = (ROOT/'maintenance/secondary-catalog-25480438.json').read_bytes()
        files['Source/SECONDARIES.md'] = (ROOT/'docs/release/SECONDARIES.md').read_bytes()
        files['Source/VALIDATION.md'] = (ROOT/'docs/release/VERIFICATION.md').read_bytes()
        files['README-zh-TW.md'] = ('''# 副武器原生投射物候選 0.1.3

這是本機開發候選，尚未完成全部副武器機制，也沒有新增玩法驗證。
目標：遊戲 build 25480438；Bingus Shared Loader v17、API 1、internal 16。

## 安裝

1. 關閉遊戲。Arsenal 內停用／移除舊自命中方案，清除舊部署。
2. 將本 ZIP 匯入 Arsenal，啟用並重新部署；需要相容的 Bingus Shared Loader。
3. 本獨立包與四選一整合包是替代安裝方式，只啟用其中一個。
4. 回退時關閉遊戲、停用本包、清除部署，再匯入原版本並重新部署。

同包包含完全不變的 P-11 0.2.1。新增副武器的來源清單在建置時由固定參考資料產生，
不新增遊戲內分類掃描。霰彈與多彈丸仍排除，Bushwhacker 也不在來源候選中。

16 個來源 ID 是原生槽位候選，不是 16 把已驗證成功的武器。
Dagger 光束、Crisper 噴射尚未支援；Warrant、P33、內部 Hornet 的 entity 後續鏈待驗證。
榴彈本體碰撞與爆炸效果必須分開驗證。完整狀態見 Source/SECONDARIES.md；
本次檢查記錄見 Source/VALIDATION.md。

未知遊戲／loader 版本維持停用。離線收集與後續開發使用 Update Toolkit 1.3.1，
其 Source/P11-Enhanced/ 內有完整可建置源碼和 AGENTS.md。
本包不會自行部署或上傳；預覽發布不代表「全部可射擊副武器」功能已完成。
''').encode('utf-8')
    target = ROOT / 'dist' / f'{stem}-{version}-build25480438-CANDIDATE.zip'
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            item = zipfile.ZipInfo(name, (2026, 9, 26, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            z.writestr(item, data)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
    return {'scope': scope, 'path': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'native_hook': False, 'self_damage_verified': False, 'runtime_tested': False,
            'p11_changed': False, 'deployed': False}


if __name__ == '__main__':
    print(json.dumps([build(s) for s in SCOPES], indent=2))

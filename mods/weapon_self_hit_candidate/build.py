"""Build two independent, unverified Arsenal candidate ZIPs; never deploy."""
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

BASE = json.loads((HERE.parent / 'p11_self_hit_dataonly' / 'profile.json').read_text(encoding='utf-8'))
PISTOLS = {
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
    'pistols': ('Pistol Series Self-Hit Candidate', 'weapon_self_hit_pistols'),
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
    p.update(id='weapon-self-hit-candidate-0.1.1-25480438-' + scope,
             version='0.1.1-candidate', scope=scope,
             resource='mods/weapon_self_hit/' + scope,
             manager_guid=str(uuid.uuid5(uuid.NAMESPACE_URL, 'P11-Enhanced/weapon-self-hit-candidate/' + scope)),
             pistol_unit_hashes=list(PISTOLS.values()),
             pistol_mapping_source='Offline mod archive index, 2026-09-01; not current-build gameplay proof',
             gameplay_verified=False, self_damage_verified=False)
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
                   'Expanded self-damage and coexistence unverified. Choose one of the three variants.')
    manifest = {'Version': 1, 'Guid': p['manager_guid'], 'Name': title,
                'Description': description,
                'Options': [{'Name': 'Enable ' + title,
                             'Description': 'Includes unchanged P-11 0.2.1. Install only one of the three self-hit variants.',
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
             'Source/VALIDATION.md': (HERE / 'VALIDATION.md').read_bytes()}
    target = ROOT / 'dist' / f'{stem}-0.1.1-build25480438-CANDIDATE.zip'
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

"""Build the byte-preserved preview.8 unified cursor addon; no deployment/publication.

Run from a complete HD2-Projectile-Collision-Filter source tree using Python 3.10+ standard library.
Dependencies: tools/{resource_archive,build_self_hit_release,verify_secondary_catalog}.py,
the preserved p11_self_hit_dataonly profile/adapters, weapon_self_hit_candidate profile
generator, maintenance catalog/filter, and patches/25480438/manifest.json. ZIPs include
the editable runtime and generated profile; this builder is run from project source.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGINAL = HERE.parent / 'p11_self_hit_dataonly'
sys.path.insert(0, str(ROOT / 'tools'))
from resource_archive import make_archive, lua_resources
from build_self_hit_release import zip_files, canonical_public_bytes

VERSION = 'v0.3.0-preview.8'
GUID = 'ad4dbb99-b77a-48ad-b56c-b75b50d66ca6'
RESOURCE = 'mods/p11/self_hit_dataonly'
ARCHIVE = '9ba626afa44a3aa3.patch_0'
NAME = f'Projectile-Collision-Filter-{VERSION}-build25480438.zip'
OUT = ROOT / 'dist'
SCOPES = ('p11', 'pistols', 'native_no_shotguns', 'native_weapons')
CHOICES = (
    ('p11', 'P11', 'P11-Self-Hit-DataOnly-0.2.4-build25480438-CANDIDATE.zip', 'P-11 Only / 僅治療手槍',
     'P-11 healing darts only. Recommended; selected by default.\n僅讓 P-11 治療飛鏢對自己生效。推薦，首次預選。'),
    ('pistols', 'Pistols', 'weapon_self_hit_pistols-0.2.0-build25480438-CANDIDATE.zip', 'All Sidearms / 手槍全部',
     'P-11 and supported sidearm projectiles. Excludes shotgun and multi-projectile types. Beam/spray unsupported; some entity paths remain unverified.\n包含 P-11 與支援的副武器投射物；排除霰彈及多彈丸。光束／噴射尚未支援，部分實體分支仍待驗證。'),
    ('native_no_shotguns', 'NativeNoShotguns', 'weapon_self_hit_native_no_shotguns-0.2.0-build25480438-CANDIDATE.zip', 'All Weapons (No Shotguns) / 全部武器不包括霰彈槍',
     'P-11 and supported native weapon projectiles. Excludes shotgun and multi-projectile types.\n包含 P-11 與支援的原生武器投射物；排除霰彈及多彈丸。'),
    ('native_weapons', 'NativeWeapons', 'weapon_self_hit_native-0.2.0-build25480438-CANDIDATE.zip', 'All Weapons (Including Shotguns) / 全部武器包括霰彈槍',
     'Includes shotgun and multi-projectile types. WARNING: May cause severe performance impact.\n包含霰彈及多彈丸。警告：可能造成嚴重性能影響。'),
)
MOD_NAME = 'Projectile Collision Filter / 投射物碰撞過濾器'
SCOPE_NAME = 'Effect Scope / 生效範圍'
SCOPE_DESCRIPTION = ('Choose one scope. P-11 Only is selected by default. Close the game before changing options, then redeploy.\n'
                     '四選一，首次預選「僅治療手槍」。切換前關閉遊戲，選好後重新部署。')
MOD_DESCRIPTION = ('Four selectable self-hit scopes using one cursor handler. The first three exclude shotguns/multishot. The fourth may cause severe performance impact. Supported native projectiles only; beam/spray and some special mechanisms are not supported. Teammate homing is installed separately. Preview release; build 25480438, Bingus Shared Loader v17 / API 1 / internal 16.\n'
                   '四選一自命中整合包，共用單一游標處理流程。前三項排除霰彈／多彈丸；第四項可能造成嚴重性能影響。僅支援原生投射物，光束／噴射與部分特殊機制尚未支援。隊友追蹤另外安裝。預覽版，適用 build 25480438、Bingus Shared Loader v17 / API 1 / internal 16。')
# Immutable payload identities from the user-accepted local candidate. Packaging
# changes must never turn an altered runtime into the same verified release.
ACCEPTED_CANDIDATE_SHA256 = '5e82ee422e68aa0778ebda26203a239032f86c44b983222bcf0433e390404e17'
ACCEPTED_PAYLOADS = {
    'p11': {'lua_sha256': '2164b3c4d2cd55bc0ea290ed71efdf9548db59247bdeaab34e96ddc321a70741', 'archive_sha256': '92a0008961aa0684e744794a10b5a51bd45bfea9f1318bb2901c231cd453cf8e'},
    'pistols': {'lua_sha256': 'bebe19a1c069416f96c9e597b6a4294b922bd06fabd824fe70c55c0bc842767c', 'archive_sha256': '412ab6871294142768cac29c33a6d1466a46260c3eb9ff705fca1a7643192809'},
    'native_no_shotguns': {'lua_sha256': 'c1f7aebdd12d690f53965874aa52ca027ead4e5ec05ee69da7c9e4a47d2e7a74', 'archive_sha256': '2cf678ac5daf1b8af55fad53cb862373f3e618c805e8707701369397f9122466'},
    'native_weapons': {'lua_sha256': 'a3f7a01cf382fff63e8cbedb7d803029f5a34b3858278cfcac9c44fb345ee964', 'archive_sha256': 'e28702004f4ebf8995a91ed9456a9ec9306afb48cccff5a6c3fdfd53e58996e4'},
}


def selector_manifest():
    return {'Version': 1, 'Guid': GUID, 'Name': MOD_NAME,
            'Description': MOD_DESCRIPTION,
            'Options': [{'Name': SCOPE_NAME, 'Description': SCOPE_DESCRIPTION,
                         'SubOptions': [{'Name': label, 'Description': description,
                                         'Include': ['Variants/' + folder]}
                                        for _, folder, _, label, description in CHOICES]}]}

CURSOR_ANCHORS = [
    {'name': 'native_cursor_read', 'rva': 0x13a986a, 'bytes_hex': '8b4130'},
    {'name': 'native_cursor_slot_mask', 'rva': 0x13a989b, 'bytes_hex': '4181e4ff070000'},
    {'name': 'native_cursor_write', 'rva': 0x13a98f4, 'bytes_hex': '895130'},
]
RUNTIME_FILES = ('core.lua', 'version.lua', 'image_windows.lua', 'data_windows.lua', 'entry.lua')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def lua(value):
    if value is True: return 'true'
    if value is False: return 'false'
    if value is None: return 'nil'
    if isinstance(value, str): return json.dumps(value, ensure_ascii=True)
    if isinstance(value, (int, float)): return str(value)
    if isinstance(value, list): return '{' + ','.join(map(lua, value)) + '}'
    if isinstance(value, dict):
        return '{' + ','.join('[' + lua(k) + ']=' + lua(v) for k, v in sorted(value.items())) + '}'
    raise TypeError(type(value))


def expanded_builder():
    spec = importlib.util.spec_from_file_location('preserved_expanded_profile_generator',
                                                HERE.parent / 'weapon_self_hit_candidate/build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile(scope):
    assert scope in SCOPES, 'Unsupported scope'
    if scope == 'p11':
        p = json.loads((ORIGINAL / 'profile.json').read_bytes())
    else:
        p = copy.deepcopy(expanded_builder().profile(scope))
    for key in tuple(p):
        if key.endswith('_verified') or key.endswith('_tested'):
            p[key] = False
    p.update(
        id=f'projectile-collision-filter-preview8-25480438-{scope}',
        version='0.2.4-candidate' if scope == 'p11' else '0.2.0-candidate',
        release_version=VERSION, scope=scope, resource=RESOURCE,
        cursor_anchors=copy.deepcopy(CURSOR_ANCHORS),
        exclude_shotguns=scope != 'native_weapons',
        p11_runtime_version='0.2.4-candidate', unified_cursor_handler=True,
        gameplay_verified=False, performance_gameplay_verified=False,
        pre_collision_timing_verified=False, runtime_tested=False,
        self_damage_verified=False, all_secondary_mechanisms_supported=False,
    )
    if scope == 'p11':
        p['excluded_projectile_types'] = {}
        p['pistol_unit_hashes'] = []
    return p


def bundle(scope):
    p = profile(scope)
    baseline = json.loads((ROOT / 'patches/25480438/manifest.json').read_bytes())
    assert p['game_sha256'] == baseline['target']['game_dll_sha256'].lower()
    assert p['exe_sha256'] == baseline['target']['executable_sha256'].lower()
    assert p['loaded_section_indices'] == [1, 2, 3, 4]
    assert len(p['code_anchors']) == 12 and len(p['cursor_anchors']) == 3
    # The reviewed Windows read/write adapters must remain byte-for-byte intact.
    for name in ('image_windows.lua', 'data_windows.lua'):
        assert (HERE / name).read_bytes() == (ORIGINAL / name).read_bytes(), name + ' changed'
    checked = [p['sections'][i - 1] for i in p['loaded_section_indices']]
    rvas = [0x3326468, 0x346bf98, 0x33266d8, 0x3326dc0, 0x347cea8, 0x37c7670 + 4096 * 8]
    for rva in rvas + [a['rva'] for a in p['code_anchors'] + p['cursor_anchors']]:
        assert any(s['rva'] <= rva and rva + 8 <= s['rva'] + s['virtual_size'] for s in checked)
    text = '-- HD2-Addon: ' + RESOURCE + '\n-- Unified cursor data-only candidate; this package gameplay is unverified.\n'
    for symbol, name in [('Core', 'core.lua'), ('Version', 'version.lua'),
                         ('MakeImage', 'image_windows.lua'), ('MakeData', 'data_windows.lua'),
                         ('Entry', 'entry.lua')]:
        text += 'local ' + symbol + '=(function()\n' + (HERE / name).read_text(encoding='utf-8') + '\nend)()\n'
    text += 'return Entry(Core,Version,MakeImage,MakeData,' + lua(p) + ',_G)\n'
    for forbidden in ('VirtualProtect', 'VirtualAlloc', 'FlushInstructionCache', 'CreateRemoteThread',
                      'OpenProcess', 'GetAsyncKeyState'):
        assert forbidden not in text, 'Unexpected capability: ' + forbidden
    assert text.count('kernel.WriteProcessMemory(process,ptr(at),desired,2,got)') == 1
    assert text.count('pcall(Core.tick,api,Profile)') == 1
    assert text.count('-- HD2-Addon: ') == 1
    return text.encode('utf-8'), p


def runtime_files(source, p):
    files = {
        'Source/projectile_collision_filter.lua': source,
        'Source/profile.json': json_bytes(p),
        'Source/VALIDATION.md': (HERE / 'VALIDATION.md').read_bytes(),
        'Source/runtime/build.py': (HERE / 'build.py').read_bytes(),
        'Source/runtime/README.md': (HERE / 'README.md').read_bytes(),
        'Source/projectile-exclusions.json': (ROOT / 'maintenance/projectile-exclusions-25480438.json').read_bytes(),
        'Source/secondary-catalog.json': (ROOT / 'maintenance/secondary-catalog-25480438.json').read_bytes(),
        'Source/SECONDARIES.md': (ROOT / 'docs/release/SECONDARIES.md').read_bytes(),
    }
    for name in RUNTIME_FILES:
        files['Source/runtime/' + name] = (HERE / name).read_bytes()
    # Source copies use Git checkout line endings. The actual bundled Lua and
    # native archives above remain pinned to the accepted candidate bytes.
    files = {name: canonical_public_bytes(name, data) for name, data in files.items()}
    files['Source/source-integrity.json'] = json_bytes({
        name.removeprefix('Source/'): sha(data) for name, data in sorted(files.items())
    })
    return files


def build(output=None, standalones=False):
    output = Path(output) if output is not None else OUT
    output = output.resolve()
    protected = (ROOT / 'dist/candidates').resolve()
    if output == protected or protected in output.parents:
        raise ValueError('Historical candidate directories are immutable; use dist or build output')
    output.mkdir(parents=True, exist_ok=True)
    files, payloads, assets = {}, {}, []
    for scope, folder, filename, label, description in CHOICES:
        source, p = bundle(scope)
        archive = make_archive(RESOURCE, source)
        if {'lua_sha256': sha(source), 'archive_sha256': sha(archive)} != ACCEPTED_PAYLOADS[scope]:
            raise ValueError('Accepted runtime payload changed: ' + scope)
        parsed, = lua_resources(io.BytesIO(archive), len(archive))
        assert parsed['body'] == source and parsed['declaration'] == RESOURCE
        include = 'Variants/' + folder
        for suffix, body in (('', archive), ('.stream', b''), ('.gpu_resources', b'')):
            files[include + '/' + ARCHIVE + suffix] = body
        for name, data in runtime_files(source, p).items():
            files['Source/' + folder + '/' + name.removeprefix('Source/')] = data
        payloads[folder] = {'scope': scope, **ACCEPTED_PAYLOADS[scope]}
        if standalones:
            single = runtime_files(source, p)
            single.update({'manifest.json': json_bytes({'Version': 1, 'Guid': p['manager_guid'],
                'Name': MOD_NAME + ' — ' + label, 'Description': description,
                'Options': [{'Name': label, 'Description': SCOPE_DESCRIPTION, 'Include': ['Addon']}]}),
                'README.md': canonical_public_bytes('README.md', (HERE / 'README.md').read_bytes()),
                'Addon/' + ARCHIVE: archive, 'Addon/' + ARCHIVE + '.stream': b'',
                'Addon/' + ARCHIVE + '.gpu_resources': b''})
            path = output / filename
            zip_files(path, single)
            assets.append({'name': filename, 'scope': scope, 'bytes': path.stat().st_size,
                           'sha256': sha(path.read_bytes()), **ACCEPTED_PAYLOADS[scope]})
    files.update({'manifest.json': json_bytes(selector_manifest()),
                  'README.md': canonical_public_bytes('README.md', (HERE / 'README.md').read_bytes()),
                  'Source/payloads.json': json_bytes(payloads)})
    target = output / NAME
    zip_files(target, files)
    assets.insert(0, {'name': NAME, 'scope': 'selector', 'bytes': target.stat().st_size,
                     'sha256': sha(target.read_bytes()), 'manager_guid': GUID})
    report = {'version': VERSION, 'status': 'preview', 'selector': NAME, 'assets': assets,
              'accepted_candidate_sha256': ACCEPTED_CANDIDATE_SHA256,
              'payloads': payloads, 'same_core_in_all_scopes': True, 'one_addon_per_scope': True,
              'native_hook': False, 'deployed': False, 'published': False,
              'user_reported_four_scope_success': True, 'comprehensive_gameplay_verified': False,
              'performance_gameplay_verified': False}
    (output / 'BUILD-preview8.json').write_bytes(json_bytes(report))
    return report


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-standalones', action='store_true',
                        help='Also build four non-public comparison packages under build/preview8-mods')
    args = parser.parse_args()
    result = build(ROOT / 'build/preview8-mods' if args.local_standalones else None,
                   standalones=args.local_standalones)
    print(json.dumps(result, ensure_ascii=False, indent=2))

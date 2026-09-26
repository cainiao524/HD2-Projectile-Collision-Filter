"""Verify the pinned offline sidearm catalog. No download, process access or writes.

The reference data is from Filediver, not proof of the installed game's plaintext.
The catalog selects loadout sidearms, then records their separate firing mechanisms.
"""
import argparse
import collections
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / 'maintenance' / 'secondary-catalog-25480438.json'
PIN = 'bf0ce329db3cf0043994eb717ea86433c303cb36'
SOURCES = {
    'generated_entities.dl_bin': (46612588, '21377252b81fdbc670eba1e59a8ab64b170323df208f175e708992e4c1fb515e'),
    'dl_library.dl_typelib': (1062658, '4d04870d0a0d4dc1284998c72cdfa6f8ff6d21aba0e36b6f758c6f73dd0417a4'),
    'generated_entity_deltas.dl_bin': (349570, '3fadc7c2475558000f9e8ad30e01d52caea481e1633e35674ed2864572694f4e'),
}
P11 = 'd6b1fb05b9109353'
BUSHWHACKER = '2b28e17ffed05f7c'
COMPONENTS = ('EquipmentComponent', 'UnitComponent', 'ProjectileWeaponComponent',
              'BeamWeaponComponent', 'ArcWeaponComponent', 'SprayWeaponComponent',
              'WeaponDataComponent', 'WieldableComponent', 'LoadoutPackageComponent',
              'LoadoutEntryComponent', 'WeaponMagazineComponent', 'WeaponChargeComponent',
              'FireSourceComponent', 'MeleeAttackComponent')
FIRING = ('ProjectileWeaponComponent', 'BeamWeaponComponent', 'ArcWeaponComponent', 'SprayWeaponComponent')
COUNTS = {'all_loadout': 193, 'loadout_by_type': {'1': 57, '2': 44, '3': 27, '4': 27, '5': 3, '6': 35},
          'sidearm': 27, 'shootable_sidearm': 20,
          'sidearm_mechanisms': {'native_from_customization_unverified': 5, 'native_projectile_unverified': 10,
                                'entity_projectile_unverified': 3, 'no_known_firing_component': 7,
                                'spray_unsupported': 1, 'beam_unsupported': 1}}
POLICY = {'loadout_type': 3, 'loadout_type_name': 'LoadoutItemType_SidearmWeapon',
          'shootable_requires_any_component': list(FIRING), 'exclude_shotguns_and_multishot': True,
          'excluded_weapon_entities': [BUSHWHACKER], 'p11_managed_separately': P11,
          'native_handler_requires': 'ProjectileWeaponComponent',
          'unsupported_handlers': ['BeamWeaponComponent', 'ArcWeaponComponent', 'SprayWeaponComponent'],
          'unknown_game_build_disables_runtime': True}
PROOF_FIELDS = ('entity', 'unit', 'category', 'loadout_type', 'components', 'projectile_type',
                'projectile_entity', 'record_evidence', 'shootable', 'mechanism')
# Fingerprint of all 27 derived proof records and complete loadout counts; names are presentation metadata.
EXPECTED_PROOF_SHA256 = '785d85ec34cd4d22bca2a4bef940419b3687fe2b1c61d47f70c7f1b781ad0970'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dl_hash(name):
    value = 5381
    for char in name:
        value = (value * 33 + ord(char)) & 0xffffffff
    return (value - 5381) & 0xffffffff


def proof_digest(rows, counts):
    value = {'rows': [{key: row[key] for key in PROOF_FIELDS} for row in sorted(rows, key=lambda r: r['entity'])],
             'counts': counts}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load_catalog(path=None):
    catalog = json.loads(Path(path or DEFAULT_CATALOG).read_text(encoding='utf-8'))
    require(catalog.get('schema_version') == 1 and catalog.get('target_build') == '25480438', 'unsupported secondary catalog schema/build')
    require(catalog.get('reference_commit') == PIN, 'secondary reference commit mismatch')
    require(catalog.get('matches_game_build') is False and catalog.get('gameplay_verified') is False,
            'offline secondary catalog must not claim current-build or gameplay verification')
    require(catalog.get('policy') == POLICY, 'secondary selection policy mismatch')
    require(catalog.get('counts') == COUNTS, 'secondary catalog completeness/count mismatch')
    require(catalog.get('proof_sha256') == EXPECTED_PROOF_SHA256, 'secondary declared proof fingerprint mismatch')
    for name, (size, digest) in SOURCES.items():
        source = catalog.get('sources', {}).get(name, {})
        require(source.get('size') == size and source.get('sha256') == digest, 'secondary reference fingerprint mismatch: ' + name)
        require(source.get('url') == f'https://raw.githubusercontent.com/xypwn/filediver/{PIN}/datalibrary/{name}.gz', 'secondary reference URL mismatch')
    rows = catalog.get('entries', [])
    require(len(rows) == 27 and len({row['entity'] for row in rows}) == 27, 'secondary catalog must retain all 27 sidearm entries')
    for row in rows:
        require(row['loadout_type'] == 3, 'non-sidearm in catalog')
        require(len(row['entity']) == len(row['unit']) == 16 and row['unit'] != '0' * 16, 'invalid entity/unit identity')
        int(row['entity'], 16); int(row['unit'], 16)
        require(row['shootable'] == any(name in row['components'] for name in FIRING), 'incorrect firing-component classification')
    require(proof_digest(rows, catalog['counts']) == EXPECTED_PROOF_SHA256, 'secondary catalog proof changed; regenerate and review against pinned sources')
    require(len(runtime_hashes(catalog)) == 16, 'secondary runtime candidate count mismatch')
    return catalog


def runtime_hashes(catalog):
    """Select native-handler candidate identities; membership is not mechanism support."""
    return sorted({row['unit'] for row in catalog['entries']
                   if row['loadout_type'] == 3 and row['shootable']
                   and 'ProjectileWeaponComponent' in row['components']
                   and row['unit'] not in (P11, BUSHWHACKER)
                   and not any(name in row['components'] for name in POLICY['unsupported_handlers'])})


def read_reference(path, name):
    expected_size, expected_hash = SOURCES[name]
    path = Path(path)
    require(path.stat().st_size <= expected_size + 1024 * 1024, 'reference input too large: ' + name)
    raw = path.read_bytes()
    if raw.startswith(b'\x1f\x8b'):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(expected_size + 1)
    require(len(raw) == expected_size and hashlib.sha256(raw).hexdigest() == expected_hash,
            'reference fingerprint mismatch: ' + name + '; encrypted installed files and other versions are not accepted')
    return raw


def derive_catalog(entities, schema, deltas):
    """Derive every sidearm record from verified .gz/plain reference file paths."""
    e = read_reference(entities, 'generated_entities.dl_bin')
    b = read_reference(schema, 'dl_library.dl_typelib')
    delta = read_reference(deltas, 'generated_entity_deltas.dl_bin')
    magic, version, tc, ec, mc, evc, eac, default_size, string_size = struct.unpack_from('<4s8I', b)
    require((magic, version) == (b'LTLD', 4), 'unsupported typelib header')
    type_offset = 36 + 4 * (tc + ec)
    member_offset = type_offset + 36 * tc + 32 * ec
    require(member_offset + 72 * mc + 16 * evc + 8 * eac + default_size + string_size == len(b), 'typelib range mismatch')
    types = {}
    for i, identity in enumerate(struct.unpack_from(f'<{tc}I', b, 36)):
        d = struct.unpack_from('<9I', b, type_offset + i * 36)
        require(d[7] + d[6] <= mc, 'typelib member range invalid')
        fields = []
        for j in range(d[6]):
            m = struct.unpack_from('<18I', b, member_offset + (d[7] + j) * 72)
            fields.append({'type': m[4], 'atom': m[3] & 255, 'count': m[3] >> 16, 'offset': m[10], 'size': m[6]})
        types[identity] = {'size': d[3], 'members': fields}
    indices, blocks = {}, {}
    at, has_index = 0, False
    while at < len(e):
        if has_index:
            index = struct.unpack_from('<I', e, at)[0]; at += 4
        unused, magic, version, kind, size, width = struct.unpack_from('<I4sIIIB', e, at)
        require(magic == b'LDLD' and width == 1 and at + 28 + size <= len(e), 'invalid entity instance')
        if has_index:
            require(index not in indices, 'duplicate component index')
            indices[index] = kind
        require(kind not in blocks, 'duplicate component block')
        blocks[kind] = (at, e[at + 28:at + 28 + size])
        at += 28 + size
        if at < len(e): has_index = e[at + 4:at + 8] != b'LDLD'
    require(at == len(e), 'entity instance range mismatch')
    require(delta[4:8] == b'LDLD' and struct.unpack_from('<I', delta, 12)[0] == dl_hash('ComponentEntityDeltaStorage'), 'invalid delta header')
    ho, hc, so, sc, co, cc, do, dc, bo, bc = struct.unpack_from('<10Q', delta, 28)
    for offset, count, stride in ((ho, hc, 16), (so, sc, 8), (co, cc, 12), (do, dc, 12), (bo, bc, 1)):
        require(28 + offset + count * stride <= len(delta), 'delta array outside input')
    patches = {}
    for i in range(hc):
        key, index = struct.unpack_from('<QI', delta, 28 + ho + i * 16)
        if not key: continue
        require(index < sc, 'delta settings index invalid')
        count, first = struct.unpack_from('<II', delta, 28 + so + index * 8)
        require(first + count <= cc, 'delta component range invalid')
        for j in range(count):
            ci, first_delta, count_delta = struct.unpack_from('<III', delta, 28 + co + (first + j) * 12)
            require(ci in indices and first_delta + count_delta <= dc, 'delta component index invalid')
            for k in range(count_delta):
                offset, size, data = struct.unpack_from('<III', delta, 28 + do + (first_delta + k) * 12)
                require(data + size <= bc, 'delta bytes outside data array')
                patches.setdefault((key, indices[ci]), []).append((offset, delta[28 + bo + data:28 + bo + data + size]))
    tables, records = {}, {}
    for name in COMPONENTS:
        kind, data_kind = dl_hash(name), dl_hash(name + 'Data')
        fields = types[data_kind]['members']
        require(len(fields) >= 2 and fields[0]['type'] == dl_hash('ComponentIndexData') and fields[1]['type'] == kind,
                'component table schema mismatch: ' + name)
        require(fields[0]['atom'] == fields[1]['atom'] == 2, 'expected inline component arrays')
        base, raw = blocks[data_kind]; size = types[kind]['size']
        require(fields[0]['offset'] + fields[0]['count'] * 16 <= len(raw), 'component hashmap outside block')
        table, evidence = {}, {}
        for i in range(fields[0]['count']):
            key, index = struct.unpack_from('<QI', raw, fields[0]['offset'] + i * 16)
            if not key: continue
            offset = fields[1]['offset'] + index * size
            require(index < fields[1]['count'] and key not in table and offset + size <= len(raw), 'invalid component record')
            value = bytearray(raw[offset:offset + size]); changes = patches.get((key, data_kind), [])
            for target, chunk in changes:
                require(target + len(chunk) <= len(value), 'component delta exceeds record')
                value[target:target + len(chunk)] = chunk
            table[key] = bytes(value)
            evidence[key] = {'hashmap_index': i, 'data_index': index, 'file_offset': base + 28 + offset,
                             'size': size, 'delta_count': len(changes)}
        tables[name], records[name] = table, evidence
    loadout_fields = [m for m in types[dl_hash('LoadoutEntryComponent')]['members'] if m['type'] == dl_hash('LoadoutItemType')]
    equipment_fields = [m for m in types[dl_hash('EquipmentComponent')]['members'] if m['type'] == dl_hash('EquipmentType')]
    require(len(loadout_fields) == len(equipment_fields) == 1 and loadout_fields[0]['offset'] == 4 and equipment_fields[0]['offset'] == 128,
            'reference classification layout mismatch')
    rows, loadout_counts = [], collections.Counter()
    for key, raw in sorted(tables['LoadoutEntryComponent'].items()):
        loadout = struct.unpack_from('<I', raw, 4)[0]; loadout_counts[str(loadout)] += 1
        if loadout != 3: continue
        require(key in tables['EquipmentComponent'] and key in tables['UnitComponent'], 'sidearm missing equipment/unit evidence')
        unit = struct.unpack_from('<Q', tables['UnitComponent'][key])[0]
        require(unit != 0, 'sidearm has no unit')
        projectile = tables['ProjectileWeaponComponent'].get(key)
        row = {'entity': f'{key:016x}', 'unit': f'{unit:016x}',
               'category': struct.unpack_from('<I', tables['EquipmentComponent'][key], 128)[0], 'loadout_type': loadout,
               'components': [name for name in COMPONENTS if key in tables[name]],
               'projectile_type': struct.unpack_from('<I', projectile)[0] if projectile is not None else None,
               'projectile_entity': f'{struct.unpack_from("<Q", projectile, 40)[0]:016x}' if projectile is not None else None,
               'record_evidence': {name: records[name][key] for name in COMPONENTS if key in records[name]}}
        row['shootable'] = any(name in row['components'] for name in FIRING)
        if 'BeamWeaponComponent' in row['components']: row['mechanism'] = 'beam_unsupported'
        elif 'SprayWeaponComponent' in row['components']: row['mechanism'] = 'spray_unsupported'
        elif 'ArcWeaponComponent' in row['components']: row['mechanism'] = 'arc_unsupported'
        elif projectile is not None:
            row['mechanism'] = ('entity_projectile_unverified' if row['projectile_entity'] != '0' * 16 else
                                'native_from_customization_unverified' if row['projectile_type'] == 0 else 'native_projectile_unverified')
        else: row['mechanism'] = 'no_known_firing_component'
        rows.append(row)
    counts = {'all_loadout': len(tables['LoadoutEntryComponent']), 'loadout_by_type': dict(loadout_counts),
              'sidearm': len(rows), 'shootable_sidearm': sum(r['shootable'] for r in rows),
              'sidearm_mechanisms': dict(collections.Counter(r['mechanism'] for r in rows))}
    require(counts == COUNTS, 'derived reference completeness mismatch')
    return {'entries': rows, 'counts': counts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=DEFAULT_CATALOG)
    parser.add_argument('--check', action='store_true', help='validate the shipped catalog (also the default)')
    parser.add_argument('--entities', type=Path, help='pinned plaintext/generated_entities.dl_bin, or its .gz')
    parser.add_argument('--schema', type=Path, help='pinned plaintext/dl_library.dl_typelib, or its .gz')
    parser.add_argument('--deltas', type=Path, help='pinned plaintext/generated_entity_deltas.dl_bin, or its .gz')
    args = parser.parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
        inputs = (args.entities, args.schema, args.deltas)
        require(all(inputs) or not any(inputs), '--entities, --schema and --deltas must be provided together')
        if all(inputs):
            derived = derive_catalog(*inputs)
            require(proof_digest(derived['entries'], derived['counts']) == EXPECTED_PROOF_SHA256, 'reference replay differs from shipped catalog')
        print(json.dumps({'ok': True, 'raw_reference_replayed': all(inputs), 'sidearm_entries': 27,
                          'shootable_sidearms': 20, 'runtime_candidates': 16,
                          'matches_game_build': False, 'gameplay_verified': False}, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, struct.error, EOFError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

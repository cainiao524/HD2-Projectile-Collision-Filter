"""Reference family membership is separate from runtime and gameplay coverage."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_secondary_catalog import load_catalog, runtime_hashes, read_reference, P11, BUSHWHACKER


class SecondaryCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()

    def changed(self, edit):
        catalog = copy.deepcopy(self.catalog)
        edit(catalog)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'catalog.json'
            path.write_text(json.dumps(catalog), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_catalog(path)

    def test_full_reference_roster_and_runtime_subset_are_distinct(self):
        entries = self.catalog['entries']
        self.assertEqual(len(entries), 27)
        self.assertEqual(sum(e['shootable'] for e in entries), 20)
        ids = runtime_hashes(self.catalog)
        self.assertEqual(len(ids), 16)
        self.assertEqual(ids, sorted(set(ids)))
        self.assertFalse(self.catalog['matches_game_build'])
        self.assertFalse(self.catalog['gameplay_verified'])
        # These have firing components, but the native writer does not implement them.
        for unit in ('7b06196e90154c88', '3f92ba65ef65cca9'):
            row = next(e for e in entries if e['unit'] == unit)
            self.assertTrue(row['shootable'])
            self.assertNotIn(unit, ids)
        self.assertNotIn(P11, ids)
        self.assertNotIn(BUSHWHACKER, ids)

    def test_old_pistols_and_new_native_candidates_are_present(self):
        ids = set(runtime_hashes(self.catalog))
        original = {'05e4e5c2db6e44a2', '8d3d52a3b2f19402', '3575aabc5f1f9326',
                    'c780bcd79547da0f', 'cf8934ff6567a42d', '1a437158e1b8d2a1',
                    'dbb6c961c59fadc1', '4d58c77087b774c5'}
        self.assertTrue(original <= ids)
        self.assertEqual(ids - original, {'0b882808c6f498e8', '416d053372c4e433',
            '52e4334e6a128caf', '9eb160830321bfd6', 'aa69a60d74a3ec54',
            'bde1f2534280300d', '14d5d4506056c7a4', 'e91f569c2ad8af01'})
        self.assertNotIn('a6a735accb4a327f', ids)  # Stalwart's AI EquipmentType is misleading.

    def test_identity_change_with_same_count_is_rejected(self):
        self.changed(lambda c: c['entries'][0].update(unit='aaaaaaaaaaaaaaaa'))

    def test_incomplete_roster_is_rejected(self):
        self.changed(lambda c: c['entries'].pop())

    def test_duplicate_identity_is_rejected(self):
        self.changed(lambda c: c['entries'].__setitem__(0, copy.deepcopy(c['entries'][1])))

    def test_policy_cannot_enable_shotguns(self):
        self.changed(lambda c: c['policy'].update(exclude_shotguns_and_multishot=False))

    def test_reference_cannot_be_promoted_to_gameplay_or_current_build(self):
        for field in ('matches_game_build', 'gameplay_verified'):
            with self.subTest(field=field):
                self.changed(lambda c: c.update({field: True}))

    def test_wrong_reference_fingerprint_is_rejected(self):
        self.changed(lambda c: c['sources']['generated_entities.dl_bin'].update(sha256='0' * 64))

    def test_missing_or_changed_mechanism_proof_is_rejected(self):
        self.changed(lambda c: c['entries'][0].update(projectile_type=999))

    def test_unknown_or_packed_binary_input_is_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'entities.bin'
            path.write_bytes(b'packed or unknown build')
            with self.assertRaisesRegex(ValueError, 'fingerprint'):
                read_reference(path, 'generated_entities.dl_bin')

    def test_built_profile_uses_catalog_and_keeps_legacy_resources_separate(self):
        spec = importlib.util.spec_from_file_location('secondary_candidate_build',
            ROOT / 'mods/weapon_self_hit_candidate/build.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        profile = builder.profile('pistols')
        self.assertEqual(profile['pistol_unit_hashes'], runtime_hashes(self.catalog))
        self.assertEqual(profile['version'], '0.1.3-candidate')
        self.assertFalse(profile['all_secondary_mechanisms_supported'])
        self.assertEqual(profile['secondary_catalog_sha256'], hashlib.sha256(
            (ROOT / 'maintenance/secondary-catalog-25480438.json').read_bytes()).hexdigest())
        self.assertEqual(len(profile['excluded_projectile_types']), 38)
        self.assertEqual(profile['resource'], 'mods/weapon_self_hit/pistols')
        self.assertEqual(builder.profile('native_weapons')['version'], '0.1.2-candidate')
        self.assertEqual(builder.profile('native_no_shotguns')['version'], '0.1.2-candidate')


if __name__ == '__main__':
    unittest.main()

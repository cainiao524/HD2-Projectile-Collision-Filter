import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from resource_archive import make_archive,lua_resources
import offline_update as collector
from test_diagnostics import pe_fixture
from offline_locator import locate

class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.game=self.root/'steamapps/common/Helldivers 2'
        (self.game/'bin').mkdir(parents=True);(self.game/'data/game').mkdir(parents=True)
        for p in ['bin/helldivers2.exe','data/game/game.dll']:(self.game/p).write_bytes(pe_fixture())
        self.manifest=self.root/'steamapps/appmanifest_553850.acf'
        self.manifest.write_text('"AppState" { "appid" "553850" "buildid" "25480438" "StateFlags" "4" "LastOwner" "76561199999999999" }')
    def tearDown(self):self.temp.cleanup()
    def collect(self,**kw):return collector.snapshot(self.game,self.root/'result',profiles=[],**kw)
    def test_stable_collection_has_binaries_sections_and_no_account(self):
        result=self.collect()
        self.assertTrue(result['complete']);self.assertFalse(result['runtime_verified'])
        self.assertTrue((self.root/'result/binaries/game.dll').exists())
        self.assertEqual(len(result['build']['files']['game_dll']['pe']['sections']),1)
        self.assertNotIn('76561199999999999',json.dumps(result))
        self.assertNotIn('LastOwner',json.dumps(result))
    def test_update_in_progress_is_incomplete(self):
        self.manifest.write_text(self.manifest.read_text().replace('"4"','"1026"'))
        self.assertFalse(self.collect()['complete'])
    def test_game_output_rejected(self):
        with self.assertRaises(ValueError):collector.snapshot(self.game,self.game/'diagnostics')
        self.assertFalse((self.game/'diagnostics').exists())
    def test_changes_during_collection(self):
        original=collector.safe_copy
        def changed(source,target,watched,expected=None):
            info=original(source,target,watched,expected)
            if Path(source).name=='game.dll':Path(source).write_bytes(b'changed')
            return info
        with patch.object(collector,'safe_copy',side_effect=changed):result=self.collect()
        self.assertFalse(result['complete'])
    def test_raw_logs_are_not_copied(self):
        logs=self.root/'logs';logs.mkdir()
        (logs/'BingusSharedLoader.log').write_text('SteamID 76561199999999999\nERROR: module not found C:/PrivateFixture/name\n')
        result=self.collect(logs=logs)
        self.assertEqual(len(result['log_reports']),1)
        self.assertNotIn('76561199999999999',json.dumps(result))
        self.assertNotIn('C:/PrivateFixture',json.dumps(result))
        self.assertFalse(result['log_reports'][0]['proves_current_build'])
    def test_unmarked_override_hides_older_addon(self):
        name='mods/stim_homing/acquisition_test'
        old=make_archive(name,'-- HD2-Addon: '+name+'\n-- StimHomingAcquisitionTest\n')
        newer=make_archive(name,'return {}\n')
        (self.game/'data/9ba626afa44a3aa3.patch_2').write_bytes(old)
        (self.game/'data/9ba626afa44a3aa3.patch_10').write_bytes(newer)
        result=self.collect();records=result['deployed']['resources']
        self.assertEqual(len(records),1);self.assertFalse(records[0]['winning_resource'])
        self.assertEqual(result['deployed']['active_gameplay_resources'],[])
    def test_readonly_research_is_not_classified_as_self_hit(self):
        name='mods/p11_research/code_capture_25480438'
        body='-- HD2-Addon: '+name+'\n-- conflicting names: StimSelfHitExperimental01 HealingPistolEnhanced\n'
        (self.game/'data/9ba626afa44a3aa3.patch_1').write_bytes(make_archive(name,body))
        logs=self.root/'logs';logs.mkdir();(logs/'P11ReadOnlyCapture.log').write_text('COMPLETE: research only\n')
        result=self.collect(logs=logs)
        self.assertEqual(result['deployed']['resources'][0]['roles'],['p11_addon','research_capture'])
        self.assertEqual(result['deployed']['active_gameplay_resources'],[])
        self.assertFalse(result['deployed']['possible_gameplay_conflict'])
        self.assertEqual(len(result['log_reports']),1)
        self.assertFalse(result['log_reports'][0]['proves_current_build'])
    def test_missing_dll_is_incomplete(self):
        (self.game/'data/game/game.dll').unlink()
        self.assertFalse(self.collect()['complete'])
    def test_dataonly_addon_is_gameplay_but_not_runtime_proof(self):
        name='mods/p11/self_hit_dataonly'
        body='-- HD2-Addon: '+name+'\n-- experimental flag writer\n'
        (self.game/'data/9ba626afa44a3aa3.patch_1').write_bytes(make_archive(name,body))
        result=self.collect()
        self.assertEqual(result['deployed']['resources'][0]['roles'],['p11_addon','self_hit'])
        self.assertFalse(result['deployed']['resources'][0]['uses_code_patch_api'])
        self.assertFalse(result['runtime_verified'])
    def test_owned_observer_is_research_and_log_is_never_gameplay_proof(self):
        name='mods/p11_research/owned_projectile_observer_25480438'
        body='-- HD2-Addon: '+name+'\n-- conflicting names: StimSelfHitExperimental01 HealingPistolEnhanced\n'
        (self.game/'data/9ba626afa44a3aa3.patch_1').write_bytes(make_archive(name,body))
        logs=self.root/'logs';logs.mkdir()
        (logs/'P11OwnedProjectileObserver.log').write_text('COMPLETE: samples=100 output=probe.jsonl; read-only observations, not a healing test\n')
        result=self.collect(logs=logs)
        self.assertEqual(result['deployed']['resources'][0]['roles'],['p11_addon','research_capture'])
        self.assertEqual(result['deployed']['active_gameplay_resources'],[])
        self.assertFalse(result['deployed']['possible_gameplay_conflict'])
        self.assertEqual(len(result['log_reports']),1)
        self.assertFalse(result['log_reports'][0]['proves_current_build'])
    def test_invalid_archive_is_incomplete(self):
        (self.game/'data/9ba626afa44a3aa3.patch_1').write_bytes(b'bad')
        self.assertFalse(self.collect()['complete'])
    def test_cache_never_claimed_current_build(self):
        cache=self.root/'cache';cache.mkdir();(cache/'projectile_settings.json').write_text('{}')
        result=self.collect(schema_dirs=[cache])
        self.assertFalse(result['schema_sources'][0]['matches_game_build'])
    def test_collection_not_promoted_to_verified_baseline(self):
        previous={'build':{'files':{}},'runtime_verified':True}
        result=self.collect(previous=previous)
        self.assertFalse(result['previous_collection_comparison']['verified_baseline'])

class ArchiveTests(unittest.TestCase):
    def test_roundtrip_and_no_execution(self):
        text=b'-- HD2-Addon: mods/test/entry\nerror("must not execute")\n'
        data=make_archive('mods/test/entry',text)
        result=list(lua_resources(io.BytesIO(data),len(data)))
        self.assertEqual(result[0]['body'],text)
    def test_hash_mismatch_rejected(self):
        data=make_archive('mods/test/wrong',b'-- HD2-Addon: mods/test/entry\nreturn {}')
        with self.assertRaises(ValueError):list(lua_resources(io.BytesIO(data),len(data)))

class LocatorTests(unittest.TestCase):
    def test_unique_match_is_never_runtime_proof(self):
        pattern=bytes(range(16));data=b'\xff'*32+pattern
        result=locate(data,[{'raw_offset':32,'raw_size':16,'rva':4096,'characteristics':0x60000020,'name':'.text'}],pattern.hex())
        self.assertEqual(result['candidates'][0]['rva'],4096)
        self.assertEqual(result['status'],'unique_unverified_candidate')
        self.assertFalse(result['can_enable_feature']);self.assertFalse(result['runtime_verified'])
    def test_duplicate_or_non_executable_matches(self):
        pattern=bytes(range(16));data=pattern*2
        section={'raw_offset':0,'raw_size':32,'rva':4096,'characteristics':0x60000020,'name':'.text'}
        self.assertEqual(locate(data,[section],pattern.hex())['status'],'ambiguous_candidates')
        section['characteristics']=0x40000040
        self.assertEqual(locate(data,[section],pattern.hex())['status'],'offline_bytes_absent')
    def test_truncated_and_out_of_range(self):
        data=bytearray(make_archive('mods/test/entry',b'return {}'))
        struct.pack_into('<Q',data,104+16,len(data)+100)
        with self.assertRaises(ValueError):list(lua_resources(io.BytesIO(data),len(data)))

if __name__=='__main__':unittest.main()

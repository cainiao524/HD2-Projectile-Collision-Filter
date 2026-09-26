import io
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile
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
    def test_renamed_selectable_package_is_found_in_downloads(self):
        downloads=self.root/'Downloads';downloads.mkdir()
        name='Projectile-Collision-Filter-v0.3.0-preview.5-build25480438.zip'
        with zipfile.ZipFile(downloads/name,'w') as archive:
            archive.writestr('manifest.json',json.dumps({'Name':'Projectile Collision Filter'}))
        output=self.root/'cli-diagnostics'
        with patch.object(Path,'home',return_value=self.root),patch.object(sys,'argv',
            ['offline_update.py','--game',str(self.game),'--output',str(output),'--logs',str(self.root/'empty-logs')]):
            self.assertEqual(collector.main(),0)
        latest=json.loads((output/'latest.json').read_bytes())
        result=json.loads((output/latest['folder']/'report.json').read_bytes())
        self.assertTrue(any(item['file']==name for item in result['packages']))
        self.assertFalse(result['runtime_verified'])
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
        self.assertEqual(result['schema_sources'][0]['source_kind'],'local_cache')
        self.assertIsNone(result['schema_sources'][0]['observed_steam_build_id'])
    def test_installed_catalogs_are_found_without_schema_arguments(self):
        for name in collector.INSTALLED_SCHEMA_NAMES:
            (self.game/'data/game'/name).write_bytes(('fixture '+name).encode())
        # The collector must neither recurse nor copy similarly named files.
        nested=self.game/'data/game/nested';nested.mkdir()
        (nested/'generated_entities.dl_bin').write_bytes(b'not collected')
        (self.game/'data/game/generated_entities.dl_bin.bak').write_bytes(b'not collected')
        result=self.collect()
        self.assertTrue(result['complete'])
        self.assertEqual({item['file'] for item in result['schema_sources']},collector.INSTALLED_SCHEMA_NAMES)
        for item in result['schema_sources']:
            original=self.game/'data/game'/item['file']
            self.assertEqual(item['source_kind'],'installed_game_data')
            self.assertEqual(item['source_relative_path'],'data/game/'+item['file'])
            self.assertEqual(item['observed_steam_build_id'],'25480438')
            self.assertEqual(item['sha256'],hashlib.sha256(original.read_bytes()).hexdigest())
            self.assertEqual((self.root/'result'/item['evidence_file']).read_bytes(),original.read_bytes())
            self.assertFalse(item['matches_game_build'])
            self.assertIn('unverified',item['provenance'])
        self.assertFalse(any('Installed catalog evidence unavailable:' in gap for gap in result['gaps']))
    def test_catalog_path_deduplication_keeps_installed_provenance(self):
        installed=self.game/'data/game'
        (installed/'generated_entities.dl_bin').write_bytes(b'installed')
        cache=self.root/'cache';cache.mkdir()
        (cache/'generated_entities.dl_bin').write_bytes(b'cached')
        result=self.collect(schema_dirs=[installed,installed/'..'/'game',cache,cache])
        self.assertEqual(len(result['schema_sources']),2)
        self.assertEqual([item['source_kind'] for item in result['schema_sources']],
                         ['installed_game_data','local_cache'])
        self.assertEqual(len({item['evidence_file'] for item in result['schema_sources']}),2)
    def test_catalog_change_between_hash_and_copy_is_incomplete_even_if_stat_restored(self):
        target=self.game/'data/game/generated_entities.dl_bin';target.write_bytes(b'before')
        original=collector.safe_copy
        def changed(source,destination,watched,expected=None):
            if Path(source)==target:
                self.assertEqual(expected,hashlib.sha256(b'before').hexdigest())
                before=target.stat();target.write_bytes(b'after!')
                os.utime(target,ns=(before.st_atime_ns,before.st_mtime_ns))
            return original(source,destination,watched,expected)
        with patch.object(collector,'safe_copy',side_effect=changed): result=self.collect()
        self.assertFalse(result['complete'])
        self.assertEqual(result['schema_sources'],[])
        self.assertTrue(any(item['item']==target.name and 'changed between inspection' in item['error']
                            for item in result['errors']))
    def test_catalog_change_after_copy_is_incomplete(self):
        target=self.game/'data/game/dl_library.dl_typelib';target.write_bytes(b'before')
        original=collector.safe_copy
        def changed(source,destination,watched,expected=None):
            info=original(source,destination,watched,expected)
            if Path(source)==target:target.write_bytes(b'after changing')
            return info
        with patch.object(collector,'safe_copy',side_effect=changed): result=self.collect()
        self.assertFalse(result['complete'])
        self.assertTrue(any(item['item']==target.name and 'changed or disappeared' in item['error']
                            for item in result['errors']))
    def test_catalog_appearing_mid_collection_is_incomplete(self):
        target=self.game/'data/game/generated_entity_deltas.dl_bin'
        original=collector.safe_copy
        def appeared(source,destination,watched,expected=None):
            info=original(source,destination,watched,expected)
            if Path(source).name=='game.dll':target.write_bytes(b'new file from update')
            return info
        with patch.object(collector,'safe_copy',side_effect=appeared):result=self.collect()
        self.assertFalse(result['complete'])
        self.assertTrue(any(item['item']==target.name for item in result['errors']))
    def test_missing_installed_catalog_is_precise_gap_not_collection_failure(self):
        cache=self.root/'cache';cache.mkdir()
        (cache/'generated_entities.dl_bin').write_bytes(b'old cache')
        result=self.collect(schema_dirs=[cache])
        self.assertTrue(result['complete'])
        for name in collector.INSTALLED_SCHEMA_NAMES:
            self.assertTrue(any('data/game/'+name in gap and 'cached copy does not establish' in gap
                                for gap in result['gaps']))
    def test_catalog_size_limits_are_bounded_before_hashing(self):
        self.assertEqual(collector.SCHEMA_SIZE_LIMITS['generated_entities.dl_bin'],256*1024*1024)
        self.assertTrue(all(size==64*1024*1024 for name,size in collector.SCHEMA_SIZE_LIMITS.items()
                            if name!='generated_entities.dl_bin'))
        target=self.game/'data/game/generated_entities.dl_bin';target.write_bytes(b'too large')
        with patch.dict(collector.SCHEMA_SIZE_LIMITS,{'generated_entities.dl_bin':2}):
            result=self.collect()
        self.assertFalse(result['complete'])
        self.assertFalse((self.root/'result/schemas').exists())
        self.assertTrue(any(item['item']==target.name and 'collection limit' in item['error']
                            for item in result['errors']))
    def test_collection_not_promoted_to_verified_baseline(self):
        previous={'build':{'files':{}},'runtime_verified':True}
        result=self.collect(previous=previous)
        self.assertFalse(result['previous_collection_comparison']['verified_baseline'])

class SchemaComparisonTests(unittest.TestCase):
    def report(self,rows):
        return {'build':{'files':{}},'deployed':{'resources':[]},'schema_sources':rows}
    def row(self,name,sha,kind='installed_game_data'):
        return {'file':name,'source_kind':kind,
                'source_relative_path':('data/game/' if kind=='installed_game_data' else '')+name,
                'sha256':sha,'evidence_file':'schemas/'+sha[:12]+'/'+name}
    def test_installed_catalog_changes_map_to_expanded_features(self):
        for name in sorted(collector.INSTALLED_SCHEMA_NAMES-{'generated_projectile_settings.dl_bin'}):
            with self.subTest(name=name):
                before=self.row(name,'a'*64);after=self.row(name,'b'*64)
                result=collector.changes_from(self.report([before]),self.report([after]))
                self.assertFalse(result['verified_baseline'])
                self.assertEqual(result['changes'],[{
                    'item':'schema_data','source_kind':'installed_game_data',
                    'source_relative_path':'data/game/'+name,
                    'before_sha256s':['a'*64],'after_sha256s':['b'*64],
                    'evidence_files_before':[before['evidence_file']],
                    'evidence_files_after':[after['evidence_file']],
                    'affected_features':['pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit']}])
    def test_projectile_changes_affect_p11_and_all_expanded_scopes(self):
        before=self.row('generated_projectile_settings.dl_bin','a'*64)
        after=self.row('generated_projectile_settings.dl_bin','b'*64)
        result=collector.changes_from(self.report([before]),self.report([after]))
        self.assertEqual(result['changes'][0]['affected_features'],
                         ['self_heal','pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit'])
    def test_legacy_cache_record_compares_without_reclassifying_it(self):
        before={'file':'projectile_settings.json','sha256':'a'*64,
                'evidence_file':'schemas/old/projectile_settings.json'}
        after=self.row('projectile_settings.json','a'*64,'local_cache')
        result=collector.changes_from(self.report([before]),self.report([after]))
        self.assertEqual(result['changes'],[])
        installed=self.row('projectile_settings.json','a'*64)
        result=collector.changes_from(self.report([before]),self.report([after,installed]))
        self.assertEqual(len(result['changes']),1)
        self.assertEqual(result['changes'][0]['source_kind'],'installed_game_data')
        self.assertEqual(result['changes'][0]['before_sha256s'],[])
    def test_multiple_cache_versions_are_preserved_and_order_independent(self):
        old=self.row('generated_entities.dl_bin','a'*64,'local_cache')
        other=self.row('generated_entities.dl_bin','b'*64,'local_cache')
        result=collector.changes_from(self.report([old,other]),self.report([other,old]))
        self.assertEqual(result['changes'],[])
        result=collector.changes_from(self.report([old,other]),self.report([other]))
        self.assertEqual(result['changes'][0]['before_sha256s'],['a'*64,'b'*64])
        self.assertEqual(result['changes'][0]['after_sha256s'],['b'*64])
    def test_missing_schema_list_in_legacy_report_is_supported(self):
        previous={'build':{'files':{}},'deployed':{'resources':[]}}
        result=collector.changes_from(previous,self.report([]))
        self.assertEqual(result['changes'],[])
        self.assertFalse(result['verified_baseline'])


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

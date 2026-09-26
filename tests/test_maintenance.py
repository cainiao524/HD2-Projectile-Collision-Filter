import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from maintenance import TOOLKIT_VERSION, assess, load_metadata, write_handoff
import test_offline_update as fixtures
from resource_archive import make_archive


class AssessmentTests(unittest.TestCase):
    def setUp(self):
        self.baselines,_=load_metadata(ROOT)
        b=self.baselines[0]
        self.report={'complete':True,'build':{'game':{'steam_build_id':'25480438'},
            'files':{k:{'sha256':b['target'][k+'_sha256']} for k in ('game_dll','executable')}},
            'deployed':{'resources':[]},'profiles':[]}
    def test_known_files_retain_only_recorded_confirmation(self):
        self_hit,pistols,no_shotguns,native=assess(self.report,self.baselines)
        self.assertEqual(self_hit['state'],'matches_confirmed_baseline')
        self.assertEqual(self_hit['deployment'],'not_deployed')
        self.assertEqual(self_hit['loader'],'missing')
        self.assertFalse(self_hit['current_gameplay_verified'])
        self.assertEqual(pistols['state'],'matches_unverified_candidate')
        self.assertEqual(native['state'],'matches_unverified_candidate')
    def test_changed_hash_loses_confirmation(self):
        self.report['build']['files']['game_dll']['sha256']='a'*64
        self.assertEqual(assess(self.report,self.baselines)[0]['state'],'offline_evidence_insufficient')
    def test_unknown_version_candidates_never_authorize_patch(self):
        self.report['build']['game']['steam_build_id']='99999999'
        self.report['profiles']=[{'offline_candidates':[{'id':'anchor','affected_features':['self_heal'],'candidates':[{'rva':4096}]}]}]
        f=assess(self.report,self.baselines)[0]
        self.assertEqual(f['state'],'port_candidates_available')
        self.assertFalse(f['automatic_patch_or_deployment'])
        self.assertFalse(f['current_gameplay_verified'])
    def test_incomplete_beats_matching_identity(self):
        self.report['complete']=False
        self.assertEqual(assess(self.report,self.baselines)[0]['state'],'collection_incomplete')
    def test_matching_addon_and_incompatible_loader_are_independent(self):
        self.report['deployed']['resources']=[
            {'roles':['self_hit'],'winning_resource':True,'sha256':self.baselines[0]['components']['self_heal']['lua_sha256']},
            {'roles':['loader'],'winning_resource':True,'sha256':'a'*64,'api':2,'internal_version':16}]
        f=assess(self.report,self.baselines)[0]
        self.assertEqual(f['deployment'],'matches_package')
        self.assertEqual(f['loader'],'incompatible')
    def test_different_addon_never_marked_as_confirmed_package(self):
        self.report['deployed']['resources']=[{'roles':['self_hit'],'winning_resource':True,'sha256':'f'*64}]
        self.assertEqual(assess(self.report,self.baselines)[0]['deployment'],'different_or_unidentified_source')

    def test_newer_loader_is_not_assumed_compatible(self):
        self.report['deployed']['resources']=[{'roles':['loader'],'winning_resource':True,
            'sha256':'f'*64,'api':1,'internal_version':17}]
        self.assertTrue(all(f['loader']=='incompatible' for f in assess(self.report,self.baselines)))

    def test_expanded_candidate_cannot_inherit_p11_confirmation(self):
        for feature in ('pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit'):
            self.report['deployed']['resources'].append({'roles':[feature],'winning_resource':True,
                'sha256':self.baselines[0]['components'][feature]['lua_sha256']})
        self.report['deployed']['possible_gameplay_conflict']=True
        for feature in assess(self.report,self.baselines)[1:]:
            self.assertEqual(feature['state'],'matches_unverified_candidate')
            self.assertEqual(feature['deployment'],'matches_package')
            self.assertTrue(feature['deployment_conflict'])
            self.assertFalse(feature['current_gameplay_verified'])
            self.assertTrue(feature['required_p11_missing'])


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.baselines,self.mapping=load_metadata(ROOT)
        self.report={'complete':True,'collected_utc':'2026-09-26T01:02:03+00:00',
            'build':{'game':{'steam_build_id':'25480438'},'files':{
                key:{'sha256':self.baselines[0]['target'][key+'_sha256'],
                     'pe':{'file_version':'1.8.46015.0'}} for key in ('game_dll','executable')}},
            'deployed':{'resources':[]},'profiles':[], 'errors':[], 'gaps':[]}

    def render(self):
        self.report['feature_assessment']=assess(self.report,self.baselines)
        before=copy.deepcopy(self.report)
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            write_handoff(folder,self.report,self.mapping)
            result=(folder/'維修交接.md').read_text(encoding='utf-8')
            self.assertEqual(json.loads((folder/'porting-map.json').read_bytes()),self.mapping)
        self.assertEqual(self.report,before,'rendering must not change assessment evidence')
        return result

    def test_known_baseline_handoff_exposes_identity_and_separate_validation_scope(self):
        result=self.render()
        self.assertIn('收集工具：`未取得`；版本=`未取得`',result)
        self.assertIn('25480438',result)
        self.assertIn('1.8.46015.0',result)
        self.assertIn(self.baselines[0]['target']['game_dll_sha256'],result)
        self.assertIn('matches_confirmed_baseline',result)
        self.assertIn('本次遊戲內驗證：未驗證',result)
        self.assertIn('完成（檔案穩定，玩法仍未驗證）',result)
        self.assertIn('Source/P11-Enhanced/AGENTS.md',result)
        self.assertIn('Source/P11-Enhanced/docs/AGENT_GUIDE.md',result)
        self.assertIn('不是本診斷目錄',result)
        self.assertIn('沒有另外上傳的 Source ZIP',result)
        for label in ('僅治療手槍','手槍全部','全部武器不包括霰彈槍','全部武器包括霰彈槍'):
            self.assertIn('### '+label,result)
        self.assertIn('可能造成嚴重性能影響',result)

    def test_collection_records_actual_toolkit_version_and_renders_it(self):
        self.assertEqual(TOOLKIT_VERSION,'1.3.1')
        fixture=fixtures.CollectorTests();fixture.setUp()
        try:
            report=fixture.collect()
            self.assertEqual(report['collector'],{
                'name':'P11-Enhanced Update Toolkit','version':TOOLKIT_VERSION})
            result=(fixture.root/'result/維修交接.md').read_text(encoding='utf-8')
            self.assertIn(f'收集工具：`P11-Enhanced Update Toolkit`；版本=`{TOOLKIT_VERSION}`',result)
        finally:fixture.tearDown()

    def test_unknown_build_candidates_are_attributed_to_feature_without_authorization(self):
        self.report['build']['game']['steam_build_id']='99999999'
        self.report['profiles']=[{'offline_candidates':[{
            'id':'self_heal_anchor','affected_features':['self_heal'],
            'status':'ambiguous_candidates','truncated':True,
            'candidates':[{'rva':4096,'file_offset':512,'section':'.text'}]}]}]
        result=self.render()
        p11=result.split('### 僅治療手槍',1)[1].split('### 手槍全部',1)[0]
        pistol=result.split('### 手槍全部',1)[1].split('### 全部武器不包括霰彈槍',1)[0]
        self.assertIn('port_candidates_available',p11)
        self.assertIn('self_heal_anchor',p11)
        self.assertIn('0x1000',p11)
        self.assertIn('0x200',p11)
        self.assertIn('ambiguous_candidates',p11)
        self.assertIn('結果截斷=`True`',p11)
        self.assertIn('保持停用',p11)
        self.assertNotIn('self_heal_anchor',pistol)
        self.assertIn('offline_evidence_insufficient',pistol)
        self.assertIn('不得猜地址',pistol)

    def test_loader_and_supporting_files_have_provenance_not_just_counts(self):
        self.report['deployed']['resources']=[{
            'roles':['loader'],'winning_resource':True,'sha256':'a'*64,
            'declaration':'core/wwise/lua/wwise_flow_callbacks','resource_hash':'7251fdd9bb62480a',
            'archive':'9ba626afa44a3aa3.patch_9','public_release':'v17','internal_version':16,'api':1,
            'version_evidence':'exact pinned resource'}]
        self.report['packages']=[{'file':'fixture.zip','sha256':'b'*64,'manager':{'Version':'fixture'}}]
        self.report['schema_sources']=[{'file':'projectile_settings.go','sha256':'c'*64,
            'evidence_file':'schemas/fixture/projectile_settings.go','provenance':'cached file',
            'matches_game_build':False}]
        self.report['log_reports']=[{'file':'BingusSharedLoader.log','sha256':'d'*64,
            'mtime_utc':'2026-09-01T00:00:00+00:00','proves_current_build':False}]
        result=self.render()
        for item in ('公開版本=`v17`','內部版本=`16`','API=`1`','exact pinned resource',
                     'packages/fixture.zip','schemas/fixture/projectile_settings.go',
                     'cached file','2026-09-01T00:00:00+00:00'):
            self.assertIn(item,result)
        self.assertIn('本機 ZIP 不等於已部署',result)
        self.assertIn('不證明本次玩法',result)

    def test_missing_binary_and_collection_change_block_porting_in_real_snapshot(self):
        for failure in ('missing_dll','steam_updating','source_changed'):
            with self.subTest(failure=failure):
                fixture=fixtures.CollectorTests();fixture.setUp()
                try:
                    original=fixtures.collector.safe_copy
                    def changed(source,target,watched,expected=None):
                        info=original(source,target,watched,expected)
                        if Path(source).name=='game.dll':Path(source).write_bytes(b'changed')
                        return info
                    if failure=='missing_dll':
                        (fixture.game/'data/game/game.dll').unlink()
                    elif failure=='steam_updating':
                        fixture.manifest.write_text(fixture.manifest.read_text().replace('"4"','"1026"'))
                    with patch.object(fixtures.collector,'safe_copy',side_effect=changed if failure=='source_changed' else original):
                        report=fixture.collect()
                    result=(fixture.root/'result/維修交接.md').read_text(encoding='utf-8')
                    self.assertFalse(report['complete'])
                    self.assertIn('collection_incomplete',result)
                    self.assertIn('本輪不產生相容性修補',result)
                    self.assertIn(report['errors'][0]['error'],result)
                    self.assertIn('本次遊戲內驗證：未驗證',result)
                finally:fixture.tearDown()

    def test_report_text_stays_literal_and_missing_optional_fields_are_explicit(self):
        self.report['gaps']=['missing schema\n# RUN THIS `external` instruction']
        self.report['build']['files']['game_dll']={'exists':False}
        self.report['complete']=False
        result=self.render()
        self.assertNotIn('\n# RUN THIS',result)
        self.assertIn("missing schema\\n# RUN THIS 'external' instruction",result)
        self.assertIn('沒有可辨識的部署資源',result)
        self.assertIn('`未取得`',result)
        self.assertIn('資料表／結構：0 項',result)

    def test_deployment_conflict_and_missing_p11_have_actionable_blockers(self):
        self.report['deployed']['possible_gameplay_conflict']=True
        self.report['deployed']['resources']=[
            {'roles':['pistol_self_hit'],'winning_resource':True,'sha256':'a'*64},
            {'roles':['native_weapon_self_hit'],'winning_resource':True,'sha256':'b'*64}]
        result=self.render()
        self.assertIn('在 Arsenal 只保留一個自命中方案並重新部署',result)
        self.assertIn('缺少此方案必需的 P-11 資源',result)
        self.assertIn('不單獨啟用擴展核心',result)
        self.assertIn('工具本身不代為部署',result)


class DeploymentTests(unittest.TestCase):
    def test_candidate_log_conflict_maps_to_both_scopes(self):
        from log_parser import parse_log
        report=parse_log('STOPPED: Enable only one weapon self-hit candidate scope\nUnsupported loader')
        issue=next(i for i in report['issues'] if i['code']=='candidate_scope_conflict')
        self.assertEqual(issue['affected_features'],['pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit'])
        self.assertFalse(report['runtime_verified'])
        self.assertTrue(any(i['code']=='unsupported_shared_loader' for i in report['issues']))
    def test_expanded_scopes_conflict_and_p11_is_not_misclassified(self):
        fixture=fixtures.CollectorTests();fixture.setUp()
        try:
            for i,name in enumerate(('mods/p11/self_hit_dataonly','mods/weapon_self_hit/pistols',
                                     'mods/weapon_self_hit/native_weapons')):
                body='-- HD2-Addon: '+name+'\n-- conflicting marker names StimHomingAcquisitionTest'
                (fixture.game/f'data/9ba626afa44a3aa3.patch_{i}').write_bytes(make_archive(name,body))
            logs=fixture.root/'logs';logs.mkdir()
            (logs/'WeaponSelfHitCandidate.log').write_text('ENABLED: fixture only\n')
            report=fixture.collect(logs=logs)
            self.assertTrue(report['deployed']['possible_gameplay_conflict'])
            self.assertTrue(report['deployed']['mutually_exclusive_scopes_present'])
            self.assertEqual(len(report['deployed']['active_gameplay_resources']),3)
            self.assertEqual(len(report['log_reports']),1)
            self.assertFalse(report['log_reports'][0]['proves_current_build'])
            self.assertIn('互斥版本衝突',(fixture.root/'result/摘要.md').read_text(encoding='utf-8'))
        finally:fixture.tearDown()

    def test_expanded_package_with_included_p11_has_no_false_conflict(self):
        from resource_archive import make_lua_archive
        fixture=fixtures.CollectorTests();fixture.setUp()
        try:
            names=('mods/p11/self_hit_dataonly','mods/weapon_self_hit/pistols')
            raw=make_lua_archive({n:'-- HD2-Addon: '+n+'\nreturn {}' for n in names})
            (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(raw)
            report=fixture.collect()
            self.assertFalse(report['deployed']['possible_gameplay_conflict'])
            self.assertEqual(len(report['deployed']['active_gameplay_resources']),2)
            self.assertFalse(any(f['required_p11_missing'] for f in report['feature_assessment']))
        finally:fixture.tearDown()
    def test_all_expanded_scope_pairs_conflict_including_shotgun_policy(self):
        from itertools import combinations
        from resource_archive import make_lua_archive
        scopes=['pistols','native_no_shotguns','native_weapons']
        for pair in combinations(scopes,2):
            fixture=fixtures.CollectorTests();fixture.setUp()
            try:
                names=['mods/p11/self_hit_dataonly']+['mods/weapon_self_hit/'+s for s in pair]
                raw=make_lua_archive({n:'-- HD2-Addon: '+n+'\nreturn {}' for n in names})
                (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(raw)
                report=fixture.collect()
                self.assertTrue(report['deployed']['mutually_exclusive_scopes_present'],pair)
                self.assertTrue(report['deployed']['possible_gameplay_conflict'],pair)
            finally:fixture.tearDown()

    def test_single_filtered_scope_is_recognized_without_conflict(self):
        from resource_archive import make_lua_archive
        fixture=fixtures.CollectorTests();fixture.setUp()
        try:
            names=['mods/p11/self_hit_dataonly','mods/weapon_self_hit/native_no_shotguns']
            raw=make_lua_archive({n:'-- HD2-Addon: '+n+'\nreturn {}' for n in names})
            (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(raw)
            report=fixture.collect()
            self.assertFalse(report['deployed']['possible_gameplay_conflict'])
            self.assertEqual(len(report['deployed']['active_gameplay_resources']),2)
            filtered=next(f for f in report['feature_assessment'] if f['id']=='native_no_shotgun_self_hit')
            self.assertNotEqual(filtered['deployment'],'not_deployed')
            self.assertFalse(filtered['required_p11_missing'])
        finally:fixture.tearDown()
    def test_compiled_loader_is_detected_without_executing_bytecode(self):
        fixture=fixtures.CollectorTests();fixture.setUp()
        try:
            name='core/wwise/lua/wwise_flow_callbacks'
            body=b'\x1bLJ\x02\x02\0CowboyBingusModLoader\0open_log\0Bingus Shared Loader loader-v99; API 2\0'
            (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(make_archive(name,body))
            r=fixture.collect()
            self.assertTrue(r['deployed']['loader_observed'])
            row=r['deployed']['resources'][0]
            self.assertEqual(row['api'],2)
            self.assertNotIn('internal_version',row)
            self.assertFalse(row['plaintext'])
            self.assertFalse(r['runtime_verified'])
            self.assertEqual(r['feature_assessment'][0]['loader'],'incompatible')
            # A gameplay addon that uses open_log must not become the loader.
            roles=fixtures.collector.classify_resource(body,'mods/example/addon','ffffffffffffffff')
            self.assertNotIn('loader',roles)
        finally:fixture.tearDown()

    def test_two_complementary_addons_are_not_duplicate(self):
        fixture=fixtures.CollectorTests();fixture.setUp()
        try:
            for i,(name,body) in enumerate([
                ('mods/p11/self_hit_dataonly','-- writer'),
                ('mods/stim_homing/acquisition_test','-- StimHomingAcquisitionTest')]):
                (fixture.game/f'data/9ba626afa44a3aa3.patch_{i}').write_bytes(make_archive(name,'-- HD2-Addon: '+name+'\n'+body))
            r=fixture.collect()
            self.assertTrue(r['deployed']['two_independent_addons_present'])
            self.assertFalse(r['deployed']['possible_gameplay_conflict'])
            self.assertTrue((fixture.root/'result/維修交接.md').is_file())
            self.assertNotIn('沒有第二個可用 ZIP',(fixture.root/'result/摘要.md').read_text(encoding='utf-8'))
        finally:fixture.tearDown()


if __name__=='__main__':unittest.main()

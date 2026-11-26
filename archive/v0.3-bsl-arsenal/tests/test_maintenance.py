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
    def test_known_files_without_deployed_source_never_inherit_confirmation(self):
        self_hit,pistols,no_shotguns,native=assess(self.report,self.baselines)
        self.assertEqual(self_hit['state'],'offline_evidence_insufficient')
        self.assertEqual(self_hit['deployment'],'not_deployed')
        self.assertEqual(self_hit['loader'],'missing')
        self.assertFalse(self_hit['current_gameplay_verified'])
        self.assertEqual(pistols['state'],'offline_evidence_insufficient')
        self.assertEqual(native['state'],'offline_evidence_insufficient')
        self.assertIsNone(self_hit['baseline'])
        self.assertTrue(self_hit['game_identity_matches_known_package'])
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
        row=assess(self.report,self.baselines)[0]
        self.assertEqual(row['deployment'],'different_or_unidentified_source')
        self.assertEqual(row['state'],'offline_evidence_insufficient')
        self.assertIsNone(row['baseline'])

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
            self.assertEqual(feature['state'],'offline_evidence_insufficient')
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
        self.assertIn('offline_evidence_insufficient',result)
        self.assertIn('本次遊戲內驗證：未驗證',result)
        self.assertIn('完成（檔案穩定，玩法仍未驗證）',result)
        self.assertIn('Source/HD2-Projectile-Collision-Filter/AGENTS.md',result)
        self.assertIn('Source/HD2-Projectile-Collision-Filter/docs/AGENT_GUIDE.md',result)
        self.assertIn('不是本診斷目錄',result)
        self.assertIn('沒有另外上傳的 Source ZIP',result)
        for label in ('僅治療手槍','手槍全部','全部武器不包括霰彈槍','全部武器包括霰彈槍'):
            self.assertIn('### '+label,result)
        self.assertIn('可能造成嚴重性能影響',result)

    def test_collection_records_actual_toolkit_version_and_renders_it(self):
        self.assertEqual(TOOLKIT_VERSION,'1.3.2')
        fixture=fixtures.CollectorTests();fixture.setUp()
        try:
            report=fixture.collect()
            self.assertEqual(report['collector'],{
                'name':'HD2-Projectile-Collision-Filter Update Toolkit','version':TOOLKIT_VERSION})
            result=(fixture.root/'result/維修交接.md').read_text(encoding='utf-8')
            self.assertIn(f'收集工具：`HD2-Projectile-Collision-Filter Update Toolkit`；版本=`{TOOLKIT_VERSION}`',result)
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


class UnifiedPreview8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec=importlib.util.spec_from_file_location('unified_diagnostic_fixture',ROOT/'mods/projectile_collision_filter/build.py')
        cls.builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.builder)
        cls.baselines,cls.mapping=load_metadata(ROOT)

    def fixture(self,scope):
        baseline=next(b for b in self.baselines if b.get('unified_cursor') and b['components']['self_heal']['scope']==scope)
        from maintenance import resource_identity
        component=baseline['components']['self_heal']
        identity=resource_identity(component['lua_sha256'],component['resource'],self.baselines)
        loader=baseline['loader']
        report={'complete':True,'build':{'game':{'steam_build_id':'25480438'},
            'files':{k:{'sha256':baseline['target'][k+'_sha256']} for k in ('game_dll','executable')}},
            'profiles':[],'deployed':{'resources':[
                {'winning_resource':True,'sha256':component['lua_sha256'],**identity},
                {'roles':['loader'],'winning_resource':True,'sha256':loader['lua_sha256'],
                 'resource_hash':loader['resource_hash'],'api':1,'internal_version':16}]}}
        return report,baseline

    def test_four_exact_lua_sources_map_shared_resource_to_scope_without_false_conflict(self):
        for scope in self.builder.SCOPES:
            with self.subTest(scope=scope):
                source,_=self.builder.bundle(scope)
                report,baseline=self.fixture(scope)
                self.assertEqual(hashlib.sha256(source).hexdigest(),baseline['components']['self_heal']['lua_sha256'])
                fixture=fixtures.CollectorTests();fixture.setUp()
                try:
                    (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(make_archive(self.builder.RESOURCE,source))
                    result=fixture.collect()
                    deployed=result['deployed'];row=deployed['resources'][0]
                    self.assertEqual(row['scope'],scope)
                    self.assertTrue(row['unified_cursor'])
                    self.assertIn('self_hit',row['roles'])
                    self.assertEqual(len(row['roles']),2 if scope=='p11' else 3)
                    self.assertFalse(deployed['possible_gameplay_conflict'])
                    self.assertFalse(deployed['mutually_exclusive_scopes_present'])
                    self.assertEqual(len(deployed['active_gameplay_resources']),1)
                    self.assertFalse(any(f['required_p11_missing'] for f in result['feature_assessment']))
                finally: fixture.tearDown()

    def test_new_sources_select_their_baseline_not_first_legacy_match(self):
        for scope in self.builder.SCOPES:
            report,baseline=self.fixture(scope)
            for row in assess(report,list(reversed(self.baselines))):
                if row['id'] in baseline['components']:
                    self.assertEqual(row['baseline'],baseline['id'])
                    self.assertEqual(row['state'],'matches_confirmed_baseline')
                    self.assertEqual(row['deployment'],'matches_package')
                    self.assertEqual(row['assessment_blockers'],[])
                else:
                    self.assertEqual(row['deployment'],'not_deployed')
                    self.assertIsNone(row['baseline'])
                self.assertFalse(row['current_gameplay_verified'])
                self.assertFalse(row['automatic_patch_or_deployment'])

    def test_missing_changed_or_incompatible_loader_prevents_confirmation(self):
        for failure in ('missing','hash','version','api','unknown'):
            report,_=self.fixture('pistols')
            if failure=='missing': report['deployed']['resources'].pop()
            elif failure=='hash': report['deployed']['resources'][-1]['sha256']='f'*64
            elif failure=='version': report['deployed']['resources'][-1]['internal_version']=17
            elif failure=='api': report['deployed']['resources'][-1]['api']=2
            else: report['deployed']['resources'][-1].pop('internal_version')
            rows=assess(report,self.baselines)
            self.assertEqual(rows[0]['state'],'offline_evidence_insufficient',failure)
            self.assertEqual(rows[0]['deployment'],'matches_package')
            self.assertTrue(rows[0]['assessment_blockers'])
            if failure=='hash': self.assertEqual(rows[0]['loader'],'source_unidentified')

    def test_unknown_shared_resource_text_never_selects_a_scope(self):
        source,_=self.builder.bundle('native_weapons')
        changed=source+b'\n-- local edit\n'
        self.assertEqual(fixtures.collector.classify_resource(changed,self.builder.RESOURCE),['p11_addon','self_hit'])
        fixture=fixtures.CollectorTests();fixture.setUp()
        try:
            (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(make_archive(self.builder.RESOURCE,changed))
            result=fixture.collect();row=result['deployed']['resources'][0]
            self.assertIsNone(row['scope'])
            self.assertIn('unknown Lua fingerprint',row['version_evidence'])
            self.assertTrue(all(f['state']=='offline_evidence_insufficient' for f in result['feature_assessment']))
        finally: fixture.tearDown()

    def test_unknown_build_and_unstable_collection_never_inherit_confirmation(self):
        for change in ('build','hash','collection','conflict'):
            report,_=self.fixture('native_no_shotguns')
            if change=='build': report['build']['game']['steam_build_id']='999'
            elif change=='hash': report['build']['files']['executable']['sha256']='f'*64
            elif change=='collection': report['complete']=False
            else: report['deployed']['possible_gameplay_conflict']=True
            row=assess(report,self.baselines)[0]
            self.assertEqual(row['state'],'collection_incomplete' if change=='collection' else 'offline_evidence_insufficient')
            self.assertFalse(row['current_gameplay_verified'])

    def test_unified_and_legacy_expanded_addon_conflict(self):
        for scope in self.builder.SCOPES:
            source,_=self.builder.bundle(scope)
            for legacy_scope in ('pistols','native_no_shotguns','native_weapons'):
                with self.subTest(scope=scope,legacy=legacy_scope):
                    fixture=fixtures.CollectorTests();fixture.setUp()
                    try:
                        (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(make_archive(self.builder.RESOURCE,source))
                        name='mods/weapon_self_hit/'+legacy_scope
                        (fixture.game/'data/9ba626afa44a3aa3.patch_1').write_bytes(make_archive(name,'-- HD2-Addon: '+name+'\nreturn {}'))
                        result=fixture.collect()
                        self.assertTrue(result['deployed']['possible_gameplay_conflict'])
                        self.assertTrue(result['deployed']['mutually_exclusive_scopes_present'])
                        if scope=='p11': self.assertEqual(result['deployed']['duplicate_roles'],[])
                        known,_=self.fixture(scope)
                        result['build']=known['build']
                        result['deployed']['resources'].append(known['deployed']['resources'][-1])
                        row=assess(result,self.baselines)[0]
                        self.assertEqual(row['deployment'],'matches_package')
                        self.assertEqual(row['state'],'offline_evidence_insufficient')
                        self.assertIn('deployment_conflict',row['assessment_blockers'])
                    finally: fixture.tearDown()

    def test_unified_with_research_markers_conflicts_without_a_second_writer(self):
        for scope in self.builder.SCOPES:
            source,_=self.builder.bundle(scope)
            for research in ('code_capture_25480438','owned_projectile_observer_25480438'):
                with self.subTest(scope=scope,research=research):
                    fixture=fixtures.CollectorTests();fixture.setUp()
                    try:
                        (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(make_archive(self.builder.RESOURCE,source))
                        name='mods/p11_research/'+research
                        (fixture.game/'data/9ba626afa44a3aa3.patch_1').write_bytes(make_archive(name,'-- HD2-Addon: '+name+'\nreturn {}'))
                        result=fixture.collect()
                        self.assertTrue(result['deployed']['possible_gameplay_conflict'])
                        self.assertTrue(result['deployed']['unified_research_conflict'])
                        self.assertEqual(len(result['deployed']['active_gameplay_resources']),1)
                        known,_=self.fixture(scope);result['build']=known['build']
                        result['deployed']['resources'].append(known['deployed']['resources'][-1])
                        row=assess(result,self.baselines)[0]
                        self.assertEqual(row['deployment'],'matches_package')
                        self.assertEqual(row['state'],'offline_evidence_insufficient')
                        self.assertIn('deployment_conflict',row['assessment_blockers'])
                    finally: fixture.tearDown()

    def test_unified_with_separate_homing_has_no_false_conflict(self):
        for scope in self.builder.SCOPES:
            source,_=self.builder.bundle(scope)
            fixture=fixtures.CollectorTests();fixture.setUp()
            try:
                (fixture.game/'data/9ba626afa44a3aa3.patch_0').write_bytes(make_archive(self.builder.RESOURCE,source))
                name='mods/stim_homing/acquisition_test'
                (fixture.game/'data/9ba626afa44a3aa3.patch_1').write_bytes(make_archive(name,'-- HD2-Addon: '+name+'\n-- StimHomingAcquisitionTest'))
                result=fixture.collect()
                self.assertFalse(result['deployed']['possible_gameplay_conflict'])
                self.assertFalse(result['deployed']['unified_research_conflict'])
                self.assertTrue(result['deployed']['two_independent_addons_present'])
            finally: fixture.tearDown()

    def test_legacy_expanded_stays_unverified_and_old_p11_evidence_is_separate(self):
        report,baseline=self.fixture('p11')
        legacy=self.baselines[0]
        report['deployed']['resources'][0]={'winning_resource':True,'roles':['self_hit'],
            'sha256':legacy['components']['self_heal']['lua_sha256']}
        report['deployed']['resources'].append({'winning_resource':True,'roles':['pistol_self_hit'],
            'sha256':legacy['components']['pistol_self_hit']['lua_sha256']})
        rows=assess(report,self.baselines)
        self.assertEqual(rows[0]['baseline'],legacy['id'])
        self.assertEqual(rows[0]['state'],'matches_confirmed_baseline')
        self.assertEqual(rows[1]['state'],'matches_unverified_candidate')
        self.assertNotEqual(rows[0]['baseline'],baseline['id'])
        report['deployed']['resources'][0]['sha256']='f'*64
        row=assess(report,self.baselines)[1]
        self.assertEqual(row['state'],'offline_evidence_insufficient')
        self.assertIn('required_p11_source_unverified',row['assessment_blockers'])

    def test_metadata_has_all_15_guards_but_no_short_offline_scan(self):
        manifest=json.loads((ROOT/'patches/25480438/manifest.json').read_bytes())
        _,profile=self.builder.bundle('p11')
        anchors=profile['code_anchors']+profile['cursor_anchors']
        self.assertEqual(self.mapping['self_hit']['runtime_anchors'],anchors)
        self.assertEqual(len(manifest['runtime_anchors']),15)
        self.assertTrue(all(len(bytes.fromhex(l['bytes_hex']))>=16 for l in manifest['locators']))
        self.assertEqual(sum(a['offline_search_eligible'] for a in manifest['runtime_anchors']),len(manifest['locators']))
        self.assertTrue(all(f['status']=='disabled' for f in manifest['features']))


if __name__=='__main__':unittest.main()

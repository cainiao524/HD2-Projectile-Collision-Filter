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
from maintenance import assess, load_metadata
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
        self_hit,pistols,native=assess(self.report,self.baselines)
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
        for feature in ('pistol_self_hit','native_weapon_self_hit'):
            self.report['deployed']['resources'].append({'roles':[feature],'winning_resource':True,
                'sha256':self.baselines[0]['components'][feature]['lua_sha256']})
        self.report['deployed']['possible_gameplay_conflict']=True
        for feature in assess(self.report,self.baselines)[1:]:
            self.assertEqual(feature['state'],'matches_unverified_candidate')
            self.assertEqual(feature['deployment'],'matches_package')
            self.assertTrue(feature['deployment_conflict'])
            self.assertFalse(feature['current_gameplay_verified'])
            self.assertTrue(feature['required_p11_missing'])


class DeploymentTests(unittest.TestCase):
    def test_candidate_log_conflict_maps_to_both_scopes(self):
        from log_parser import parse_log
        report=parse_log('STOPPED: Enable only one weapon self-hit candidate scope\nUnsupported loader')
        issue=next(i for i in report['issues'] if i['code']=='candidate_scope_conflict')
        self.assertEqual(issue['affected_features'],['pistol_self_hit','native_weapon_self_hit'])
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

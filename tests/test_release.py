"""Package boundary tests: all variants preserve the proven P-11 resource."""
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_variants_release import build_mods, toolkit_files, source_files, public_asset_names, TOOLKIT_NAME, SELF_NAME, SELF_HASH
from resource_archive import lua_resources, make_lua_archive, make_archive
from build_selectable_mod import NAME as SELECTABLE_NAME, CHOICES, ARCHIVE

class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.packages=build_mods()

    def test_every_variant_contains_exact_working_p11(self):
        guids=set()
        for name,data in self.packages.items():
            if name == SELECTABLE_NAME:
                continue
            with self.subTest(package=name),zipfile.ZipFile(io.BytesIO(data)) as z:
                self.assertIsNone(z.testzip())
                manager=json.loads(z.read('manifest.json'));guids.add(manager['Guid'])
                self.assertEqual(manager['Options'][0]['Include'],['Addon'])
                raw=z.read('Addon/9ba626afa44a3aa3.patch_0')
                resources=list(lua_resources(io.BytesIO(raw),len(raw)))
                self.assertEqual(len(resources),1 if name==SELF_NAME else 2)
                p11=[r for r in resources if r['declaration']=='mods/p11/self_hit_dataonly']
                self.assertEqual(len(p11),1)
                self.assertEqual(hashlib.sha256(p11[0]['body']).hexdigest(),'b81d634f7fa631340d2d3a29c1b608ccdec3ee8b1d7417cb53d13e155d97483a')
                self.assertEqual(z.read('Source/p11_self_hit_dataonly.lua'),p11[0]['body'])
                self.assertFalse(any(r['resource_hash']=='7251fdd9bb62480a' for r in resources))
                if name!=SELF_NAME:
                    profile=json.loads(z.read('Source/profile.json'))
                    if profile['scope']=='native_weapons':
                        self.assertFalse(profile['exclude_shotguns'])
                        self.assertEqual(profile['excluded_projectile_types'],{})
                    else:
                        self.assertTrue(profile['exclude_shotguns'])
                        self.assertEqual(len(profile['excluded_projectile_types']),38)
                        self.assertNotIn('318',profile['excluded_projectile_types'])
        self.assertEqual(len(guids),4)
        self.assertEqual(hashlib.sha256(self.packages[SELF_NAME]).hexdigest(),SELF_HASH)

    def test_single_mod_has_four_exclusive_suboptions_with_original_payloads(self):
        with zipfile.ZipFile(io.BytesIO(self.packages[SELECTABLE_NAME])) as z:
            self.assertIsNone(z.testzip())
            manifest=json.loads(z.read('manifest.json'))
            self.assertTrue(manifest['Name'].startswith('Projectile Collision Filter '))
            self.assertEqual(len(manifest['Options']),1)
            parent=manifest['Options'][0]
            self.assertEqual(parent['Name'],'生效範圍')
            self.assertFalse(parent.get('Include'))
            self.assertEqual(len(parent['SubOptions']),4)
            self.assertEqual([item['Name'] for item in parent['SubOptions']],
                             ['僅治療手槍','手槍全部','全部武器不包括霰彈槍','全部武器包括霰彈槍'])
            self.assertIn('可能造成嚴重性能影響',parent['SubOptions'][3]['Description'])
            self.assertEqual(parent['SubOptions'][0]['Include'],['Variants/P11'])
            deployed=set()
            for choice,(folder,package,label,_) in zip(parent['SubOptions'],CHOICES):
                self.assertEqual(choice['Name'],label)
                self.assertEqual(choice['Include'],[f'Variants/{folder}'])
                with zipfile.ZipFile(io.BytesIO(self.packages[package])) as original:
                    for suffix in ('','.stream','.gpu_resources'):
                        name=f'Variants/{folder}/{ARCHIVE}{suffix}'
                        deployed.add(name)
                        self.assertEqual(z.read(name),original.read(f'Addon/{ARCHIVE}{suffix}'))
            self.assertEqual({n for n in z.namelist() if '.patch_' in n},deployed)

    def test_native_archive_table_and_payload_boundaries(self):
        items={'mods/test/a':b'-- HD2-Addon: mods/test/a\nreturn 1',
               'mods/test/b':b'-- HD2-Addon: mods/test/b\nreturn 2'}
        raw=make_lua_archive(items)
        self.assertEqual(struct.unpack_from('<III',raw),(0xF0000011,1,2))
        self.assertEqual(struct.unpack_from('<I',raw,88)[0],2)
        self.assertEqual(struct.unpack_from('<Q',raw,32)[0],len(raw))
        for index in range(2):
            at=104+80*index;offset=struct.unpack_from('<Q',raw,at+16)[0]
            self.assertEqual(struct.unpack_from('<I',raw,at+76)[0],index)
            length=struct.unpack_from('<I',raw,at+56)[0]
            self.assertEqual(offset%16,0);self.assertGreaterEqual(offset,264)
            self.assertLessEqual(offset+length,len(raw))
        self.assertEqual({r['declaration']:r['body'] for r in lua_resources(io.BytesIO(raw),len(raw))},items)
        self.assertEqual(make_lua_archive({'mods/test/a':b'x'}),make_archive('mods/test/a',b'x'))

    def test_six_downloads_and_toolkit_source_are_complete(self):
        sources=source_files()
        files=toolkit_files(sources,b'fixture',self.packages,{'runtime-licenses/test.txt':b'license'})
        self.assertEqual(set(public_asset_names()),set(self.packages)|{TOOLKIT_NAME})
        self.assertEqual(len(public_asset_names()),6)
        self.assertTrue(all(n.endswith('.zip') for n in public_asset_names()))
        self.assertEqual({n.removeprefix('Source/P11-Enhanced/'):d for n,d in files.items()
                          if n.startswith('Source/P11-Enhanced/')},sources)
        self.assertEqual(files['README.md'],sources['docs/COLLECTION.md'])
        self.assertIn('Source/P11-Enhanced/AGENTS.md',files['AGENTS.md'].decode())
        self.assertEqual(set(line.split('  ')[1] for line in files['MOD-SHA256SUMS.txt'].decode().splitlines()),set(self.packages))
        self.assertFalse(any(n.startswith(('diagnostics/','binaries/','Mods/','local-settings')) for n in files))
        self.assertFalse(any(n.endswith('.zip') for n in files))

    def test_standalone_packages_preserve_preview4_bytes(self):
        expected={
            SELF_NAME:SELF_HASH,
            'weapon_self_hit_pistols-0.1.2-build25480438-CANDIDATE.zip':'7cdb730fce4c8da0f07b5868b5d652ddeea80aee4765720de59b6f8b4d4a11f2',
            'weapon_self_hit_native_no_shotguns-0.1.2-build25480438-CANDIDATE.zip':'001888c8c614b3df53052499eee974bb7e8b47cecffdb9284c3d3af38c76ba3f',
            'weapon_self_hit_native-0.1.2-build25480438-CANDIDATE.zip':'e19b0d528d0e8cdd195918d8de8af3f555446d0991666c00e5ae91b82946c206',
        }
        for name,digest in expected.items():
            self.assertEqual(hashlib.sha256(self.packages[name]).hexdigest(),digest,name)

    def test_public_source_excludes_private_evidence(self):
        files=source_files()
        for name in files:
            self.assertFalse(name.startswith(('research/','work/','vendor/','diagnostics/','local-history/')))
            self.assertNotIn(Path(name).suffix.lower(),('.bin','.exe','.dll','.log'))
        self.assertEqual(set(json.loads(files['maintenance/baselines.json'])['baselines'][0]['components']),
                         {'self_heal','pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit'})

if __name__=='__main__':unittest.main()

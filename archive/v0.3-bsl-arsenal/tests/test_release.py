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
from build_variants_release import build_mods, toolkit_files, source_files, public_asset_names, TOOLKIT_NAME, MOD_BUILDER, SELECTABLE_NAME, CHOICES, ARCHIVE
from resource_archive import lua_resources, make_lua_archive, make_archive

class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.packages=build_mods()

    def test_every_scope_preserves_exact_accepted_runtime(self):
        self.assertEqual(set(self.packages), {SELECTABLE_NAME})
        with zipfile.ZipFile(io.BytesIO(self.packages[SELECTABLE_NAME])) as z:
            for scope, folder, _, _, _ in CHOICES:
                with self.subTest(scope=scope):
                    raw = z.read('Variants/' + folder + '/' + ARCHIVE)
                    resources = list(lua_resources(io.BytesIO(raw), len(raw)))
                    self.assertEqual(len(resources), 1)
                    self.assertEqual(resources[0]['declaration'], 'mods/p11/self_hit_dataonly')
                    expected = MOD_BUILDER.ACCEPTED_PAYLOADS[scope]
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), expected['archive_sha256'])
                    self.assertEqual(hashlib.sha256(resources[0]['body']).hexdigest(), expected['lua_sha256'])
                    self.assertEqual(z.read('Source/' + folder + '/projectile_collision_filter.lua'), resources[0]['body'])
                    profile = json.loads(z.read('Source/' + folder + '/profile.json'))
                    self.assertEqual(profile['scope'], scope)
                    self.assertEqual(profile['exclude_shotguns'], scope != 'native_weapons')
                    self.assertEqual(len(profile['code_anchors']) + len(profile['cursor_anchors']), 15)

    def test_single_mod_has_four_exclusive_bilingual_suboptions(self):
        with zipfile.ZipFile(io.BytesIO(self.packages[SELECTABLE_NAME])) as z:
            manifest = json.loads(z.read('manifest.json'))
            self.assertEqual(manifest, MOD_BUILDER.selector_manifest())
            self.assertEqual(manifest['Name'], 'Projectile Collision Filter / 投射物碰撞過濾器')
            parent = manifest['Options'][0]
            self.assertEqual(parent['Name'], 'Effect Scope / 生效範圍')
            self.assertFalse(parent.get('Include'))
            self.assertEqual(len(parent['SubOptions']), 4)
            self.assertEqual(parent['SubOptions'][0]['Include'], ['Variants/P11'])
            self.assertIn('selected by default', parent['Description'])
            self.assertIn('首次預選', parent['Description'])
            self.assertIn('WARNING: May cause severe performance impact.', parent['SubOptions'][3]['Description'])
            self.assertIn('警告：可能造成嚴重性能影響。', parent['SubOptions'][3]['Description'])
            self.assertEqual({n for n in z.namelist() if '.patch_' in n},
                             {'Variants/' + folder + '/' + ARCHIVE + suffix
                              for _, folder, *_ in CHOICES for suffix in ('', '.stream', '.gpu_resources')})

    def test_accepted_candidate_cannot_be_overwritten(self):
        with self.assertRaisesRegex(ValueError, 'immutable'):
            MOD_BUILDER.build(ROOT / 'dist/candidates/v0.3.0-preview.8')

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

    def test_two_downloads_and_toolkit_source_are_complete(self):
        sources=source_files()
        files=toolkit_files(sources,b'fixture',self.packages,{'runtime-licenses/test.txt':b'license'})
        self.assertEqual(set(public_asset_names()),set(self.packages)|{TOOLKIT_NAME})
        self.assertEqual(len(public_asset_names()),2)
        self.assertTrue(all(n.endswith('.zip') for n in public_asset_names()))
        self.assertEqual({n.removeprefix('Source/HD2-Projectile-Collision-Filter/'):d for n,d in files.items()
                          if n.startswith('Source/HD2-Projectile-Collision-Filter/')},sources)
        self.assertEqual(files['README.md'],sources['docs/COLLECTION.md'])
        self.assertIn('Source/HD2-Projectile-Collision-Filter/AGENTS.md',files['AGENTS.md'].decode())
        self.assertEqual(set(line.split('  ')[1] for line in files['MOD-SHA256SUMS.txt'].decode().splitlines()),set(self.packages))
        self.assertFalse(any(n.startswith(('diagnostics/','binaries/','Mods/','local-settings')) for n in files))
        self.assertFalse(any(n.endswith('.zip') for n in files))

    def test_public_source_matches_git_checkout_line_endings(self):
        from build_self_hit_release import canonical_public_bytes, VERBATIM_PUBLIC_FILES
        files = source_files()
        self.assertIn(b'* text=auto eol=lf', files['.gitattributes'])
        for name, data in files.items():
            with self.subTest(name=name):
                self.assertEqual(data, canonical_public_bytes(name, data))
                if name in VERBATIM_PUBLIC_FILES:
                    self.assertEqual(data, (ROOT / name).read_bytes())
                    self.assertIn((name + ' -text').encode(), files['.gitattributes'])
                elif name.endswith('.cmd'):
                    self.assertNotIn(b'\n', data.replace(b'\r\n', b''))
                elif not name.endswith('.png'):
                    self.assertNotIn(b'\r\n', data)
        self.assertEqual(canonical_public_bytes('example.py', b'a\r\nb\n'), b'a\nb\n')
        self.assertEqual(canonical_public_bytes('example.cmd', b'a\r\nb\n'), b'a\r\nb\r\n')

    def test_public_source_excludes_private_evidence(self):
        files=source_files()
        for name in files:
            self.assertFalse(name.startswith(('research/','work/','vendor/','diagnostics/','local-history/')))
            self.assertNotIn(Path(name).suffix.lower(),('.bin','.exe','.dll','.log'))
        self.assertTrue(set(json.loads(files['maintenance/baselines.json'])['baselines'][0]['components']).issuperset(
                         {'self_heal','pistol_self_hit','native_no_shotgun_self_hit','native_weapon_self_hit'}))

if __name__=='__main__':unittest.main()

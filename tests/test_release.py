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
from build_variants_release import build_mods, collection_files, source_files, SELF_NAME, SELF_HASH
from resource_archive import lua_resources, make_lua_archive, make_archive

class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.packages=build_mods()

    def test_every_variant_contains_exact_working_p11(self):
        guids=set()
        for name,data in self.packages.items():
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
        self.assertEqual(len(guids),3)
        self.assertEqual(hashlib.sha256(self.packages[SELF_NAME]).hexdigest(),SELF_HASH)

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

    def test_collection_contains_only_explicit_inputs(self):
        files=collection_files({'P11-Update.exe':b'fixture'},self.packages,'source.zip',b'source')
        for name,data in self.packages.items(): self.assertEqual(files['Mods/'+name],data)
        self.assertFalse(any(n.startswith(('diagnostics/','binaries/','local-settings')) for n in files))
        self.assertEqual(len([n for n in files if n.startswith('Mods/')]),3)

    def test_public_source_excludes_private_evidence(self):
        files=source_files()
        for name in files:
            self.assertFalse(name.startswith(('research/','work/','vendor/','diagnostics/','local-history/')))
            self.assertNotIn(Path(name).suffix.lower(),('.bin','.exe','.dll','.log'))
        self.assertEqual(set(json.loads(files['maintenance/baselines.json'])['baselines'][0]['components']),
                         {'self_heal','pistol_self_hit','native_weapon_self_hit'})

if __name__=='__main__':unittest.main()

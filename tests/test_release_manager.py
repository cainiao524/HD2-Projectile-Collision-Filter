"""Release boundary tests: fixed assets, private data rejection, and GitHub hashes."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import release_manager as release
from resource_archive import make_lua_archive


def zip_bytes(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return output.getvalue()


class ReleaseManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from build_variants_release import build_mods
        cls.mod_packages = build_mods()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='p11-release-tests-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.files = {'AGENTS.md': b'Read README.md.\n', 'Collect-HD2-Update.cmd': b'@echo off\r\n',
                      'docs/COLLECTION.md': b'Toolkit guide.\n', 'LICENSE-NOTICE.md': b'License.\n',
                      'maintenance/baselines.json': b'{}\n', 'patches/25480438/manifest.json': b'{}\n'}
        self.files.update({'tools/' + name: b'# public source\n' for name in release.TOOLS})
        self.packages = dict(self.mod_packages)
        entries = release.read_zip(self.packages[release.SELECTABLE_NAME], 'integrated')
        raw = entries['Variants/P11/' + release.ARCHIVE]
        from resource_archive import lua_resources
        self.p11, = [item['body'] for item in lua_resources(io.BytesIO(raw), len(raw))]
        self.report = {'project': 'HD2-Projectile-Collision-Filter', 'release': release.VERSION, 'prerelease': True,
                       'public_assets': list(release.asset_roles()),
                       'source_manifest': {name: release.sha(data) for name, data in self.files.items()},
                       'assets': {name: {'bytes': len(data), 'sha256': release.sha(data)}
                                  for name, data in self.packages.items()}}
        toolkit = {'P11-Update.exe': b'MZfixture', 'Collect-HD2-Update.cmd': self.files['Collect-HD2-Update.cmd'],
                   'README.md': self.files['docs/COLLECTION.md'], 'AGENTS.md': b'Source/HD2-Projectile-Collision-Filter/AGENTS.md',
                   'LICENSE-NOTICE.md': self.files['LICENSE-NOTICE.md'],
                   'runtime-licenses/Python-LICENSE.txt': b'Python license',
                   'runtime-licenses/PyInstaller-COPYING.txt': b'PyInstaller license',
                   'MOD-SHA256SUMS.txt': ''.join(release.sha(data) + '  ' + name + '\n'
                                                for name, data in sorted(self.packages.items())).encode()}
        toolkit.update({release.SOURCE_PREFIX + name: data for name, data in self.files.items()})
        toolkit.update({name: data for name, data in self.files.items()
                        if name.startswith(('tools/', 'maintenance/', 'patches/'))})
        self.packages[release.TOOLKIT_NAME] = zip_bytes(toolkit)
        for name, data in self.packages.items():
            self.replace_asset(name, data)
        patcher = patch.object(release, 'source_files', lambda: dict(self.files))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.target = 'a' * 40

    def write_manifest(self):
        (self.directory / 'PUBLIC-ASSETS.json').write_text(json.dumps(self.report), encoding='utf-8')

    def replace_asset(self, name, data):
        self.packages[name] = data
        (self.directory / name).write_bytes(data)
        self.report['assets'][name] = {'bytes': len(data), 'sha256': release.sha(data)}
        self.write_manifest()

    def change_zip(self, name, entry, data):
        entries = release.read_zip(self.packages[name], name)
        entries[entry] = data
        self.replace_asset(name, zip_bytes(entries))

    def remote_release(self, digest=True):
        return {'tag_name': release.VERSION, 'prerelease': True, 'draft': False,
                'html_url': 'https://github.com/example/project/releases/tag/' + release.VERSION,
                'assets': [{'name': name, 'id': index + 1, 'state': 'uploaded', 'size': meta['bytes'],
                            'digest': 'sha256:' + meta['sha256'] if digest else None}
                           for index, (name, meta) in enumerate(self.report['assets'].items())]}

    def test_two_asset_fixture_verifies_without_mutating_files(self):
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        report = release.verify_release(self.directory)
        self.assertEqual(len(report['public_assets']), 2)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})

    def test_arbitrary_and_duplicate_assets_are_rejected(self):
        for names in [self.report['public_assets'] + ['private.zip'],
                      self.report['public_assets'][:-1] + [release.SELECTABLE_NAME],
                      self.report['public_assets'][:-1] + ['../private.zip']]:
            with self.subTest(names=names):
                self.report['public_assets'] = names
                self.write_manifest()
                with self.assertRaisesRegex(ValueError, 'two approved'):
                    release.verify_release(self.directory)

    def test_changed_asset_rejected_before_unpack(self):
        (self.directory / release.SELECTABLE_NAME).write_bytes(b'not the built ZIP')
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            release.verify_release(self.directory)

    def test_stale_source_snapshot_is_rejected(self):
        self.files['AGENTS.md'] = b'changed after build'
        with self.assertRaisesRegex(ValueError, 'current exportable source'):
            release.verify_release(self.directory)

    def test_private_source_files_and_paths_are_rejected(self):
        for files in [{'evidence.bin': b'private'}, {'diagnostics/summary.md': b'private'},
                      {'guide.md': ('Game at C:' + '\\Users\\Someone\\game').encode()}]:
            with self.subTest(files=files), self.assertRaises(ValueError):
                release.check_source(files)

    def test_only_exact_reviewed_cover_is_allowed_in_public_source(self):
        for name in release.KNOWN_PUBLIC_IMAGES:
            image = (ROOT / name).read_bytes()
            with self.subTest(name=name):
                release.check_source({name: image})
                with self.assertRaisesRegex(ValueError, 'Forbidden public source file type'):
                    release.check_source({'docs/assets/unreviewed.png': image})
                for wrong in (b'MZgame', image[:-1], image + b'private', image[:45] + bytes([image[45] ^ 1]) + image[46:]):
                    with self.assertRaises(ValueError):
                        release.check_source({name: wrong})

    def test_bbcode_is_public_text_with_the_same_privacy_checks(self):
        name = 'docs/release/bilingual.bbcode'
        release.check_source({name: '[b]治療手槍 / Stim Pistol[/b]\n'.encode('utf-8')})
        for data in (b'\xff\xfe', b'MZ\x00binary', ('C:' + '\\Users\\Someone\\game').encode()):
            with self.subTest(data=data), self.assertRaises(ValueError):
                release.check_source({name: data})

    def test_cover_dimensions_and_reviewed_hash_are_both_enforced(self):
        name = next(iter(release.KNOWN_PUBLIC_IMAGES))
        image = (ROOT / name).read_bytes()
        expected = release.KNOWN_PUBLIC_IMAGES[name]
        with patch.object(release, 'KNOWN_PUBLIC_IMAGES', {name: dict(expected, width=expected['width'] + 1)}):
            with self.assertRaisesRegex(ValueError, 'dimensions differ'):
                release.check_source({name: image})
        with patch.object(release, 'KNOWN_PUBLIC_IMAGES', {name: dict(expected, sha256='0' * 64)}):
            with self.assertRaisesRegex(ValueError, 'SHA-256 differs'):
                release.check_source({name: image})

    def test_toolkit_includes_exact_source_artwork_without_an_extra_asset(self):
        for name in release.KNOWN_PUBLIC_IMAGES:
            image = (ROOT / name).read_bytes()
            self.files[name] = image
            self.report['source_manifest'][name] = release.sha(image)
            self.change_zip(release.TOOLKIT_NAME, release.SOURCE_PREFIX + name, image)
        report = release.verify_release(self.directory)
        self.assertEqual(len(report['public_assets']), 2)
        self.change_zip(release.TOOLKIT_NAME, release.SOURCE_PREFIX + name, b'changed')
        with self.assertRaisesRegex(ValueError, 'Toolkit source differs'):
            release.verify_release(self.directory)

    def test_unsafe_zip_path_is_rejected_even_with_matching_asset_hash(self):
        self.change_zip(release.TOOLKIT_NAME, '../game.dll', b'private')
        with self.assertRaisesRegex(ValueError, 'Unsafe path'):
            release.verify_release(self.directory)

    def test_extra_game_binary_in_toolkit_is_rejected(self):
        self.change_zip(release.TOOLKIT_NAME, 'game.dll', b'MZgame')
        with self.assertRaisesRegex(ValueError, 'explicit public layout'):
            release.verify_release(self.directory)

    def test_toolkit_source_must_match_current_source(self):
        self.change_zip(release.TOOLKIT_NAME, release.SOURCE_PREFIX + 'AGENTS.md', b'changed')
        with self.assertRaisesRegex(ValueError, 'Toolkit source differs'):
            release.verify_release(self.directory)

    def test_selected_payload_cannot_contain_unapproved_resource(self):
        raw = make_lua_archive({'mods/p11/self_hit_dataonly': self.p11,
                               'mods/unrelated/extra': b'-- HD2-Addon: mods/unrelated/extra\nreturn {}'})
        self.change_zip(release.SELECTABLE_NAME, 'Variants/P11/' + release.ARCHIVE, raw)
        with self.assertRaisesRegex(ValueError, 'Unexpected resource identity'):
            release.verify_release(self.directory)

    def test_same_resource_with_altered_lua_is_rejected(self):
        raw = make_lua_archive({'mods/p11/self_hit_dataonly': self.p11 + b'\n-- unauthorized runtime change\n'})
        self.change_zip(release.SELECTABLE_NAME, 'Variants/P11/' + release.ARCHIVE, raw)
        with self.assertRaisesRegex(ValueError, 'Accepted unified runtime changed'):
            release.verify_release(self.directory)

    def test_scope_swap_is_rejected_even_with_valid_resource(self):
        entries = release.read_zip(self.packages[release.SELECTABLE_NAME], 'integrated')
        self.change_zip(release.SELECTABLE_NAME, 'Variants/P11/' + release.ARCHIVE,
                        entries['Variants/Pistols/' + release.ARCHIVE])
        with self.assertRaisesRegex(ValueError, 'Accepted unified runtime changed'):
            release.verify_release(self.directory)

    def test_bilingual_label_and_first_default_cannot_drift(self):
        entries = release.read_zip(self.packages[release.SELECTABLE_NAME], 'integrated')
        manifest = json.loads(entries['manifest.json'])
        manifest['Options'][0]['SubOptions'].reverse()
        self.change_zip(release.SELECTABLE_NAME, 'manifest.json', json.dumps(manifest).encode())
        with self.assertRaisesRegex(ValueError, 'Bilingual selectable manifest'):
            release.verify_release(self.directory)

    def test_hashes_are_added_to_notes_without_changing_original(self):
        text = release.notes_with_hashes('A release.\n', self.report)
        self.assertEqual(text.count(release.SHA_MARKER), 1)
        for name, meta in self.report['assets'].items():
            self.assertIn('| `' + name + '` | `' + meta['sha256'] + '` |', text)
        with self.assertRaisesRegex(ValueError, 'generated checksum'):
            release.notes_with_hashes(text, self.report)

    def test_remote_digests_also_download_both_files(self):
        remote = self.remote_release()
        by_id = {str(item['id']): self.packages[item['name']] for item in remote['assets']}
        with patch.object(release, 'gh_json', side_effect=[remote, {'sha': self.target}]), \
             patch.object(release, 'run', side_effect=lambda *args: by_id[args[-1].rsplit('/', 1)[-1]]) as command:
            result = release.verify_remote(self.directory, release.DEFAULT_REPO, self.target)
        self.assertTrue(result['sha256_verified'])
        self.assertEqual(command.call_count, 2)

    def test_missing_remote_digests_use_authenticated_downloads(self):
        remote = self.remote_release(digest=False)
        by_id = {str(item['id']): self.packages[item['name']] for item in remote['assets']}
        def download(*args):
            self.assertEqual(args[:4], ('gh', 'api', '-H', 'Accept: application/octet-stream'))
            return by_id[args[-1].rsplit('/', 1)[-1]]
        with patch.object(release, 'gh_json', side_effect=[remote, {'sha': self.target}]), \
             patch.object(release, 'run', side_effect=download) as command:
            release.verify_remote(self.directory, release.DEFAULT_REPO, self.target)
        self.assertEqual(command.call_count, 2)

    def test_remote_changed_hash_asset_set_and_tag_fail(self):
        for kind in ('hash', 'set', 'tag', 'download'):
            remote = self.remote_release(digest=kind != 'download')
            commit = self.target
            if kind == 'hash': remote['assets'][0]['digest'] = 'sha256:' + '0' * 64
            if kind == 'set': remote['assets'].pop()
            if kind == 'tag': commit = 'b' * 40
            with self.subTest(kind=kind), \
                 patch.object(release, 'gh_json', side_effect=[remote, {'sha': commit}]), \
                 patch.object(release, 'run', return_value=b'corrupted'), self.assertRaises(ValueError):
                release.verify_remote(self.directory, release.DEFAULT_REPO, self.target)

    def test_publish_revalidates_source_and_uses_only_exact_two_files(self):
        notes = self.directory / 'notes.md'
        notes.write_text('Release notes.\n', encoding='utf-8')
        def publish(*args):
            self.assertEqual(args[:4], ('gh', 'release', 'create', release.VERSION))
            self.assertEqual(set(args[4:6]), {str((self.directory / name).resolve())
                                             for name in release.asset_roles()})
            self.assertIn('--prerelease', args)
            self.assertEqual(args[args.index('--title') + 1],
                             'Projectile Collision Filter ' + release.VERSION + ' — P-11 Self-Heal / 自療・四選一')
            self.assertEqual(args[args.index('--target') + 1], self.target)
            generated = Path(args[args.index('--notes-file') + 1]).read_text(encoding='utf-8')
            self.assertIn(release.SHA_MARKER, generated)
            return b'https://github.com/example/project/releases/tag/test\n'
        with patch.object(release, 'check_git_source') as git_check, \
             patch.object(release, 'gh_json', side_effect=[{'sha': self.target}, []]), \
             patch.object(release, 'run', side_effect=publish):
            result = release.publish_release(self.directory, release.DEFAULT_REPO, self.target, notes)
        self.assertEqual(result['assets'], 2)
        git_check.assert_called_once()
        self.assertEqual(notes.read_text(), 'Release notes.\n')

    def test_publish_rejects_existing_tag_for_other_commit(self):
        with patch.object(release, 'check_git_source'), \
             patch.object(release, 'gh_json', side_effect=[{'sha': self.target},
                 [{'ref': 'refs/tags/' + release.VERSION}], {'sha': 'b' * 40}]), \
             patch.object(release, 'run') as command, self.assertRaisesRegex(ValueError, 'different commit'):
            release.publish_release(self.directory, release.DEFAULT_REPO, self.target, self.directory / 'notes.md')
        command.assert_not_called()

    def test_git_source_checks_clean_exact_committed_checkout(self):
        checkout = self.directory / 'checkout'
        checkout.mkdir()
        for name, data in self.files.items():
            path = checkout / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        responses = [str(checkout).encode(), self.target.encode(), b'',
                     ('\x00'.join(sorted(self.files)) + '\x00').encode(),
                     *[b'canonical-blob' for _ in range(len(self.files) * 2)]]
        with patch.object(release, 'run', side_effect=responses):
            release.check_git_source(checkout, self.target, self.report)
        with patch.object(release, 'run', side_effect=responses[:2] + [b' M AGENTS.md\n']), \
             self.assertRaisesRegex(ValueError, 'uncommitted'):
            release.check_git_source(checkout, self.target, self.report)
        (checkout / 'AGENTS.md').write_bytes(b'smuggled ignored change')
        with patch.object(release, 'run', side_effect=responses), \
             self.assertRaisesRegex(ValueError, 'packaged source'):
            release.check_git_source(checkout, self.target, self.report)

    def test_subprocess_failure_does_not_echo_credentials(self):
        result = subprocess.CompletedProcess(['gh'], 1, b'private response', b'credential detail')
        with patch.object(release.subprocess, 'run', return_value=result), self.assertRaises(ValueError) as caught:
            release.run('gh', 'api', 'test')
        self.assertNotIn('credential detail', str(caught.exception))
        self.assertNotIn('private response', str(caught.exception))


if __name__ == '__main__':
    unittest.main()

"""Generated public document aliases are explicit and cannot clobber tracked edits."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import sync_docs


class SyncDocsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='p11-docs-tests-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.mapping = {'docs/release/README.md': 'README.md', 'docs/release/GUIDE.md': 'docs/GUIDE.md'}
        self.write('docs/release/README.md', b'New home\n')
        self.write('docs/release/GUIDE.md', b'New guide\n')
        self.write('README.md', b'Old home\n')
        self.write('.gitignore', b'build/\n')
        self.manifest()

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def manifest(self):
        self.write('publication-files.json', json.dumps({'document_exports': self.mapping}).encode())

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.PIPE)

    def commit_fixture(self):
        if not shutil.which('git'):
            self.skipTest('Git required for tracked edit protection tests')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Document Test', '-c', 'user.email=test@example.invalid',
                 'commit', '-qm', 'Document fixture')

    def test_check_is_read_only_and_reports_missing_and_stale_aliases(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result = sync_docs.sync_documents(self.root)
        self.assertFalse(result['in_sync'])
        self.assertEqual({item['status'] for item in result['updates']}, {'missing', 'different'})
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_non_git_apply_preserves_old_bytes_and_then_checks_clean(self):
        result = sync_docs.sync_documents(self.root, apply=True)
        self.assertTrue(result['in_sync'])
        backup = self.root / result['backup']
        self.assertEqual((backup / 'previous/README.md').read_bytes(), b'Old home\n')
        self.assertEqual((self.root / 'README.md').read_bytes(), b'New home\n')
        self.assertEqual((self.root / 'docs/GUIDE.md').read_bytes(), b'New guide\n')
        self.assertTrue((backup / 'sync-record.json').is_file())
        checked = sync_docs.sync_documents(self.root)
        self.assertTrue(checked['in_sync'])
        self.assertEqual(checked['updates'], [])

    def test_clean_tracked_alias_updates_after_editing_source(self):
        self.commit_fixture()
        self.write('docs/release/README.md', b'Changed canonical source\n')
        result = sync_docs.sync_documents(self.root, apply=True)
        self.assertTrue(result['in_sync'])
        self.assertEqual((self.root / 'README.md').read_bytes(), b'Changed canonical source\n')
        self.assertEqual(self.git('diff', '--cached', '--name-only'), b'')

    def test_independent_tracked_edit_blocks_all_destinations_before_any_write(self):
        self.commit_fixture()
        self.write('README.md', b'Independent home edit\n')
        with self.assertRaisesRegex(ValueError, 'independent edits'):
            sync_docs.sync_documents(self.root, apply=True)
        self.assertEqual((self.root / 'README.md').read_bytes(), b'Independent home edit\n')
        self.assertFalse((self.root / 'docs/GUIDE.md').exists())
        self.assertFalse((self.root / 'build').exists())

    def test_staged_destination_change_is_protected(self):
        self.commit_fixture()
        self.write('README.md', b'Independent staged edit\n')
        self.git('add', 'README.md')
        self.write('README.md', b'Old home\n')
        with self.assertRaisesRegex(ValueError, 'independent edits'):
            sync_docs.sync_documents(self.root, apply=True)
        self.assertFalse((self.root / 'build').exists())

    def test_independent_tracked_deletion_is_protected(self):
        self.commit_fixture()
        (self.root / 'README.md').unlink()
        with self.assertRaisesRegex(ValueError, 'independently deleted'):
            sync_docs.sync_documents(self.root, apply=True)
        self.assertFalse((self.root / 'README.md').exists())

    def test_already_generated_uncommitted_alias_is_noop(self):
        self.commit_fixture()
        sync_docs.sync_documents(self.root, apply=True)
        result = sync_docs.sync_documents(self.root, apply=True)
        self.assertTrue(result['in_sync'])
        self.assertIsNone(result['backup'])

    def test_bad_paths_collisions_and_export_cycles_are_rejected(self):
        mappings = [ {'docs/release/README.md': '../escape.md'},
                     {'docs/release/README.md': 'docs\\escape.md'},
                     {'docs/release/README.md': '.git/README.md'},
                     {'docs/release/README.md': 'tools/script.py'},
                     {'docs/release/README.md': 'README.md', 'docs/release/GUIDE.md': 'readme.md'},
                     {'docs/release/README.md': 'docs/release/GUIDE.md', 'docs/release/GUIDE.md': 'README.md'} ]
        for mapping in mappings:
            with self.subTest(mapping=mapping):
                self.mapping = mapping
                self.manifest()
                with self.assertRaises(ValueError):
                    sync_docs.sync_documents(self.root, apply=True)
                self.assertFalse((self.root / 'build').exists())

    def test_missing_source_prevents_partial_updates(self):
        (self.root / 'docs/release/GUIDE.md').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing document source'):
            sync_docs.sync_documents(self.root, apply=True)
        self.assertEqual((self.root / 'README.md').read_bytes(), b'Old home\n')

    def test_symbolic_link_destination_is_rejected(self):
        target = self.root / 'docs/GUIDE.md'
        try:
            target.symlink_to(self.root / 'README.md')
        except OSError:
            self.skipTest('Creating symbolic links requires platform permission')
        with self.assertRaisesRegex(ValueError, 'symlink or junction'):
            sync_docs.sync_documents(self.root, apply=True)
        self.assertEqual((self.root / 'README.md').read_bytes(), b'Old home\n')

    def test_missing_git_only_blocks_existing_git_checkout(self):
        with patch.object(sync_docs, 'git_result', side_effect=FileNotFoundError):
            self.assertIsNone(sync_docs.find_git_root(self.root))
            (self.root / '.git').mkdir()
            with self.assertRaisesRegex(ValueError, 'Git is required'):
                sync_docs.find_git_root(self.root)


if __name__ == '__main__':
    unittest.main()

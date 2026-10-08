"""Importer tests use temporary local Git repositories and never access a network."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('importer_under_test', ROOT / 'import_into_repo.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)

@unittest.skipUnless(shutil.which('git'), 'Git is needed for local importer tests')
class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.bundle = base / 'bundle'
        self.bundle.mkdir()
        content = b'# Original learning guide\n'
        (self.bundle / 'README.md').write_bytes(content)
        (self.bundle / 'BUNDLE_MANIFEST.json').write_text(json.dumps({'files': {
            'README.md': hashlib.sha256(content).hexdigest()}}), encoding='utf-8')
        self.target = base / 'repo'
        self.target.mkdir()
        self.run_git('init')
        self.original = (b'# Original index\n\n'
                         b'[maplab](https://github.com/ethz-asl/mav_voxblox_planning)\n')
        (self.target / 'README.md').write_bytes(self.original)
        self.run_git('add', 'README.md')
        self.run_git('-c', 'user.name=Bundle Tests', '-c', 'user.email=tests@example.invalid',
                     '-c', 'commit.gpgsign=false', 'commit', '-m', 'Initial fixture')

    def run_git(self, *args):
        return subprocess.run(['git', '-C', str(self.target), *args],
                              check=True, text=True, capture_output=True).stdout

    def test_dry_run_is_read_only(self):
        result = importer.import_bundle(self.bundle, self.target, update_readme=True)
        self.assertFalse(result['applied'])
        self.assertFalse((self.target / 'learning').exists())
        self.assertEqual((self.target / 'README.md').read_bytes(), self.original)
        self.assertEqual(self.run_git('status', '--porcelain').strip(), '')

    def test_apply_preserves_backup_and_fixes_link(self):
        result = importer.import_bundle(self.bundle, self.target, apply=True, update_readme=True)
        dest = self.target / importer.DESTINATION
        self.assertTrue(result['applied'])
        self.assertFalse(result['github_upload_performed'])
        self.assertEqual((dest / 'provenance/README.before-import.md').read_bytes(), self.original)
        text = (self.target / 'README.md').read_text(encoding='utf-8')
        self.assertIn(importer.MARKER, text)
        self.assertIn(importer.NEW_LINK, text)
        self.assertNotIn(importer.OLD_LINK, text)
        self.assertEqual(self.run_git('rev-list', '--count', 'HEAD').strip(), '1')

    def test_default_apply_leaves_readme(self):
        importer.import_bundle(self.bundle, self.target, apply=True)
        self.assertEqual((self.target / 'README.md').read_bytes(), self.original)

    def test_dirty_checkout_rejected(self):
        (self.target / 'unrelated.txt').write_text('pending work')
        with self.assertRaises(ValueError):
            importer.import_bundle(self.bundle, self.target, apply=True)
        self.assertFalse((self.target / 'learning').exists())

    def test_existing_destination_rejected(self):
        destination = self.target / importer.DESTINATION
        destination.mkdir(parents=True)
        (destination / 'existing.md').write_text('preserve')
        self.run_git('add', '.')
        self.run_git('-c', 'user.name=Bundle Tests', '-c', 'user.email=tests@example.invalid',
                     '-c', 'commit.gpgsign=false', 'commit', '-m', 'Existing content')
        with self.assertRaises(ValueError):
            importer.import_bundle(self.bundle, self.target, apply=True)
        self.assertEqual((destination / 'existing.md').read_text(), 'preserve')

    def test_checksum_mismatch_rejected(self):
        (self.bundle / 'README.md').write_text('modified without updating hashes')
        with self.assertRaises(ValueError):
            importer.import_bundle(self.bundle, self.target, apply=True)

    def test_upstream_origin_rejected(self):
        self.run_git('remote', 'add', 'origin', 'https://github.com/alexkoven/Autonomous-UAVs.git')
        with self.assertRaises(ValueError):
            importer.import_bundle(self.bundle, self.target, apply=True)

    def test_path_traversal_rejected(self):
        (self.bundle / 'BUNDLE_MANIFEST.json').write_text(json.dumps({'files': {
            '../outside.md': 'not-a-valid-hash'}}), encoding='utf-8')
        with self.assertRaises(ValueError):
            importer.import_bundle(self.bundle, self.target, apply=True)

if __name__ == '__main__':
    unittest.main()

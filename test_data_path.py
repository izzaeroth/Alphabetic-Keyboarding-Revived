"""Tests of local storage selection and first-run records migration."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import app


class DataPathTests(unittest.TestCase):
    def test_data_directory_uses_platform_appropriate_location(self):
        # Windows uses LOCALAPPDATA; Unix-like systems use XDG_DATA_HOME.
        # Always patch the variable for the actual host OS, so this test
        # works when the Windows build script runs the suite before packing.
        with tempfile.TemporaryDirectory() as temp:
            variable = 'LOCALAPPDATA' if app.os.name == 'nt' else 'XDG_DATA_HOME'
            with patch.dict(app.os.environ, {variable: temp}):
                self.assertEqual(app.get_data_directory(), Path(temp) / 'AlphabeticKeyboardingRevived')

    def test_migration_copies_both_files_without_removing_original(self):
        with tempfile.TemporaryDirectory() as temp:
            old_dir, new_dir = Path(temp) / 'old', Path(temp) / 'new'
            old_dir.mkdir()
            (old_dir / 'progress.json').write_text(json.dumps([{'student': 'Test'}]), encoding='utf-8')
            (old_dir / 'settings.json').write_text(json.dumps({'student': 'Test'}), encoding='utf-8')
            self.assertEqual(app.migrate_existing_data(old_dir, new_dir), ['progress.json', 'settings.json'])
            self.assertEqual(json.loads((new_dir / 'progress.json').read_text()), [{'student': 'Test'}])
            self.assertTrue((old_dir / 'progress.json').exists())

    def test_migration_does_not_overwrite_newer_data(self):
        with tempfile.TemporaryDirectory() as temp:
            old_dir, new_dir = Path(temp) / 'old', Path(temp) / 'new'
            old_dir.mkdir()
            new_dir.mkdir()
            (old_dir / 'progress.json').write_text('["old"]', encoding='utf-8')
            (new_dir / 'progress.json').write_text('["new"]', encoding='utf-8')
            self.assertEqual(app.migrate_existing_data(old_dir, new_dir), [])
            self.assertEqual((new_dir / 'progress.json').read_text(), '["new"]')


if __name__ == '__main__':
    unittest.main()

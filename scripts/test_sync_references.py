import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.sync_references import synchronize


class SyncReferencesTest(unittest.TestCase):
    def test_check_detects_drift_without_writing_and_sync_repairs_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_bytes(b"canonical\n")
            stale = root / "stale.md"
            stale.write_bytes(b"stale\n")
            linked = root / "linked.md"
            linked.symlink_to(source)
            copies = {"source.md": ("stale.md", "nested/missing.md", "linked.md")}
            with patch("scripts.sync_references.COPIES", copies):
                self.assertEqual(1, synchronize(root, check=True))
                self.assertEqual(b"stale\n", stale.read_bytes())
                self.assertFalse((root / "nested").exists())
                self.assertTrue(linked.is_symlink())
                self.assertEqual(0, synchronize(root, check=False))
                self.assertEqual(0, synchronize(root, check=True))
                for destination in copies["source.md"]:
                    target = root / destination
                    self.assertFalse(target.is_symlink())
                    self.assertEqual(source.read_bytes(), target.read_bytes())
                before = stale.stat().st_mtime_ns
                self.assertEqual(0, synchronize(root, check=False))
                self.assertEqual(before, stale.stat().st_mtime_ns)
                self.assertEqual(b"canonical\n", source.read_bytes())

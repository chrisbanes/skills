import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.sync_references import COPIES, synchronize


class SyncReferencesTest(unittest.TestCase):
    def test_delivery_procedure_is_not_overwritten_by_delegated_workflow(self):
        destinations = {item for copies in COPIES.values() for item in copies}
        self.assertNotIn(
            "skills/deliver-spec/references/implementation-mode.md", destinations
        )
        self.assertIn(
            "skills/deliver-spec/references/subagent-selection.md", destinations
        )

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

    def test_rejects_source_and_parent_symlinks_before_any_writes(self):
        for linked_path in ("source.md", "sources", "copies"):
            for check in (True, False):
                with self.subTest(path=linked_path, check=check), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory) / "checkout"
                    root.mkdir()
                    outside = Path(directory) / "outside"
                    outside.mkdir()
                    (outside / "source.md").write_bytes(b"external source\n")
                    (outside / "copy.md").write_bytes(b"external copy\n")
                    (root / "local.md").write_bytes(b"canonical\n")
                    (root / "first.md").write_bytes(b"unchanged\n")
                    (root / linked_path).symlink_to(
                        outside / "source.md" if linked_path == "source.md" else outside
                    )
                    source = "local.md" if linked_path == "copies" else (
                        "source.md" if linked_path == "source.md" else "sources/source.md"
                    )
                    destination = "copies/copy.md" if linked_path == "copies" else "copy.md"
                    with patch("scripts.sync_references.COPIES", {
                        "local.md": ("first.md", destination),
                        source: ("first.md", destination),
                    }):
                        self.assertEqual(1, synchronize(root, check=check))
                    self.assertEqual(b"unchanged\n", (root / "first.md").read_bytes())
                    self.assertEqual(b"external source\n", (outside / "source.md").read_bytes())
                    self.assertEqual(b"external copy\n", (outside / "copy.md").read_bytes())
                    self.assertFalse((root / "copy.md").exists())

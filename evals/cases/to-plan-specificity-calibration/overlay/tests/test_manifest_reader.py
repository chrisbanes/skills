import unittest

from manifest_reader import missing_manifest_error


class ManifestReaderTest(unittest.TestCase):
    def test_quotes_missing_manifest_path(self):
        self.assertEqual(
            "manifest not found: 'configs/team manifest.json'",
            missing_manifest_error("configs/team manifest.json"),
        )

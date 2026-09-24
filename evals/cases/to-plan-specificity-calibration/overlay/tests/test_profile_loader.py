import unittest

from profile_loader import invalid_profile_error


class ProfileLoaderTest(unittest.TestCase):
    def test_quotes_invalid_profile_path(self):
        self.assertEqual(
            "invalid profile at 'configs/team manifest.json'",
            invalid_profile_error("configs/team manifest.json"),
        )

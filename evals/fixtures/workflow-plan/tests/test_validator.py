import unittest

from validator import missing_file_error


class ValidatorTest(unittest.TestCase):
    def test_names_missing_file(self):
        self.assertIn("settings.json", missing_file_error("settings.json"))

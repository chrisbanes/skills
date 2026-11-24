import unittest
from unittest.mock import Mock

from labels import display_labels


class DisplayLabelsTest(unittest.TestCase):
    def test_keeps_order_and_duplicates_and_skips_blank_labels(self):
        rows = iter([" beta ", "\t", " alpha", "beta", ""])
        self.assertEqual(display_labels(rows), ["beta", "alpha", "beta"])

    def test_empty_input(self):
        self.assertEqual(display_labels([]), [])

    def test_trims_each_row_once(self):
        row = Mock(wraps=" beta ")
        self.assertEqual(display_labels([row]), ["beta"])
        row.strip.assert_called_once_with()

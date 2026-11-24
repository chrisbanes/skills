import unittest
from unittest.mock import patch

from labels import display_labels


class CountedLabel(str):
    strip_calls = 0

    def strip(self, *args, **kwargs):
        self.strip_calls += 1
        return super().strip(*args, **kwargs)


class DisplayLabelsTest(unittest.TestCase):
    def test_keeps_order_and_duplicates_and_skips_blank_labels(self):
        rows = iter([" beta ", "\t", " alpha", "beta", ""])
        self.assertEqual(display_labels(rows), ["beta", "alpha", "beta"])

    def test_empty_input(self):
        self.assertEqual(display_labels([]), [])

    def test_trims_each_row_once(self):
        row = CountedLabel(" beta ")
        # Route explicit str.strip and map(str.strip, ...) through the same
        # counter as row.strip for this real string subtype.
        with patch("labels.str", CountedLabel, create=True):
            self.assertEqual(display_labels([row]), ["beta"])
        self.assertEqual(row.strip_calls, 1)

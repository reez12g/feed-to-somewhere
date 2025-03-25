"""Tests for the utils module."""

import unittest
from datetime import datetime
from src.feed_to_somewhere.utils import clean_text, format_date, chunk_text, get_current_date_iso


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""

    def test_clean_text(self):
        """Test the clean_text function with normal and invalid Unicode text."""
        # Test with normal text
        text = "Hello, World!"
        self.assertEqual(clean_text(text), text)

        # Test with invalid unicode characters
        text_with_invalid = "Hello\uD800World"
        self.assertEqual(clean_text(text_with_invalid), "HelloWorld")

    def test_format_date_with_valid_struct(self):
        """Test format_date with a valid date structure."""
        # Create a structured time object
        class PublishedTime:
            tm_year = 2023
            tm_mon = 1
            tm_mday = 1

        published_time = PublishedTime()
        default_date = "2000-01-01"

        self.assertEqual(format_date(published_time, default_date), "2023-01-01")

    def test_format_date_with_none(self):
        """Test format_date with None."""
        default_date = "2000-01-01"
        self.assertEqual(format_date(None, default_date), default_date)

    def test_format_date_with_invalid_struct(self):
        """Test format_date with an invalid structure."""
        # Create an object without the required attributes
        invalid_struct = object()
        default_date = "2000-01-01"

        self.assertEqual(format_date(invalid_struct, default_date), default_date)

    def test_chunk_text_smaller_than_chunk_size(self):
        """Test chunk_text with text smaller than chunk size."""
        text = "Short text"
        chunks = chunk_text(text, 20)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_chunk_text_larger_than_chunk_size(self):
        """Test chunk_text with text larger than chunk size."""
        text = "a" * 25
        chunks = chunk_text(text, 10)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], "a" * 10)
        self.assertEqual(chunks[1], "a" * 10)
        self.assertEqual(chunks[2], "a" * 5)

    def test_get_current_date_iso(self):
        """Test get_current_date_iso returns a date in ISO format."""
        date_str = get_current_date_iso()

        # Check if the date string is in ISO format (YYYY-MM-DD)
        try:
            datetime.fromisoformat(date_str)
            valid_format = True
        except ValueError:
            valid_format = False

        self.assertTrue(valid_format)
        self.assertEqual(len(date_str), 10)  # YYYY-MM-DD is 10 characters


if __name__ == "__main__":
    unittest.main()

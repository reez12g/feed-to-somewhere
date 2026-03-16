"""Tests for the config module."""

import unittest
from unittest.mock import patch

from feed_to_somewhere.config import Config, require_one_of, require_positive_int


class TestConfig(unittest.TestCase):
    """Test cases for configuration helpers."""

    def test_config_defaults_do_not_require_notion_env(self):
        """Test Config can be created without Notion credentials."""
        with patch.dict("os.environ", {}, clear=True):
            config = Config()

        self.assertIsNone(config.notion_token)
        self.assertIsNone(config.notion_data_source_id)
        self.assertIsNone(config.database_id)
        self.assertEqual(config.feed_list_path, "feed_list.csv")
        self.assertEqual(config.chunk_size, 2000)

    def test_config_reads_data_source_id_when_present(self):
        """Test Config reads a preferred Notion data source ID."""
        with patch.dict("os.environ", {"NOTION_DATA_SOURCE_ID": "data_source_123"}, clear=True):
            config = Config()

        self.assertEqual(config.notion_data_source_id, "data_source_123")

    def test_config_rejects_invalid_chunk_size(self):
        """Test Config rejects a non-positive chunk size."""
        with patch.dict("os.environ", {"CHUNK_SIZE": "0"}, clear=True):
            config = Config()

        with self.assertRaises(ValueError):
            _ = config.chunk_size

    def test_require_positive_int_rejects_invalid_values(self):
        """Test require_positive_int rejects invalid strings."""
        with self.assertRaises(ValueError):
            require_positive_int("abc", "CHUNK_SIZE")

    def test_require_one_of_returns_first_present_value(self):
        """Test require_one_of returns the first available candidate."""
        self.assertEqual(
            require_one_of((None, "FIRST"), ("value", "SECOND")),
            "value",
        )

    def test_require_one_of_raises_when_all_missing(self):
        """Test require_one_of raises when every candidate is missing."""
        with self.assertRaises(ValueError):
            require_one_of((None, "FIRST"), (None, "SECOND"))


if __name__ == "__main__":
    unittest.main()

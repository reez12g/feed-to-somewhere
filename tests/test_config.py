"""Tests for the config module."""

import unittest
from unittest.mock import patch

from feed_to_somewhere.config import Config, require_positive_int


class TestConfig(unittest.TestCase):
    """Test cases for configuration helpers."""

    def test_config_defaults_do_not_require_notion_env(self):
        """Test Config can be created without Notion credentials."""
        with patch.dict("os.environ", {}, clear=True):
            config = Config()

        self.assertIsNone(config.notion_token)
        self.assertIsNone(config.database_id)
        self.assertEqual(config.feed_list_path, "feed_list.csv")
        self.assertEqual(config.chunk_size, 2000)

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


if __name__ == "__main__":
    unittest.main()

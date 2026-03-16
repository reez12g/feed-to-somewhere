"""Tests for the notion_client module."""

import unittest
from unittest.mock import patch, MagicMock
from feed_to_somewhere.notion_client import NotionClient
from notion_client.errors import APIResponseError


class MockAPIResponseError(APIResponseError):
    """Minimal APIResponseError test double that avoids version-specific init args."""

    def __init__(self, message="Error message"):
        Exception.__init__(self, message)


class TestNotionClient(unittest.TestCase):
    """Test cases for the NotionClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.token = "test_token"
        self.database_id = "test_database_id"
        self.data_source_id = "test_data_source_id"

        # Create a patcher for the config
        self.config_patcher = patch("feed_to_somewhere.notion_client.config")
        self.mock_config = self.config_patcher.start()
        self.mock_config.notion_token = self.token
        self.mock_config.notion_data_source_id = self.data_source_id
        self.mock_config.database_id = self.database_id
        self.mock_config.chunk_size = 2000

        # Create a patcher for the logger
        self.logger_patcher = patch("feed_to_somewhere.notion_client.logger")
        self.mock_logger = self.logger_patcher.start()

        # Create a patcher for the Client
        self.client_patcher = patch("feed_to_somewhere.notion_client.Client")
        self.mock_client_class = self.client_patcher.start()
        self.mock_client = MagicMock()
        self.mock_client_class.return_value = self.mock_client

        # Create the NotionClient instance
        self.notion_client = NotionClient()

    def tearDown(self):
        """Tear down test fixtures."""
        self.config_patcher.stop()
        self.logger_patcher.stop()
        self.client_patcher.stop()

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        self.assertEqual(self.notion_client.token, self.token)
        self.assertEqual(self.notion_client.database_id, self.database_id)
        self.assertEqual(self.notion_client.data_source_id, self.data_source_id)
        self.assertEqual(self.notion_client.chunk_size, 2000)
        self.mock_client_class.assert_called_once_with(auth=self.token)

    def test_init_with_custom_database_values(self):
        """Test initialization with custom database values."""
        custom_token = "custom_token"
        custom_database_id = "custom_database_id"
        self.mock_config.notion_data_source_id = None
        self.mock_client.databases.retrieve.return_value = {"data_sources": [{"id": "resolved_data_source_id"}]}

        notion_client = NotionClient(token=custom_token, database_id=custom_database_id)

        self.assertEqual(notion_client.token, custom_token)
        self.assertEqual(notion_client.database_id, custom_database_id)
        self.assertEqual(notion_client.data_source_id, "resolved_data_source_id")
        self.mock_client_class.assert_called_with(auth=custom_token)
        self.mock_client.databases.retrieve.assert_called_once_with(database_id=custom_database_id)

    def test_init_with_custom_data_source_id(self):
        """Test initialization with an explicit data source ID."""
        notion_client = NotionClient(
            token="custom_token",
            database_id="custom_database_id",
            data_source_id="explicit_data_source_id",
        )

        self.assertEqual(notion_client.data_source_id, "explicit_data_source_id")
        self.mock_client.databases.retrieve.assert_not_called()

    def test_init_resolves_data_source_id_from_database(self):
        """Test initialization resolves the child data source from a database."""
        self.mock_config.notion_data_source_id = None
        self.mock_client.databases.retrieve.return_value = {"data_sources": [{"id": "resolved_data_source_id"}]}

        notion_client = NotionClient()

        self.assertEqual(notion_client.data_source_id, "resolved_data_source_id")
        self.mock_client.databases.retrieve.assert_called_once_with(database_id=self.database_id)

    def test_init_requires_a_parent_identifier(self):
        """Test initialization requires either a data source ID or a database ID."""
        self.mock_config.notion_data_source_id = None
        self.mock_config.database_id = None

        with self.assertRaises(ValueError):
            NotionClient()

    def test_init_raises_when_database_has_no_data_sources(self):
        """Test initialization raises when a database cannot resolve a data source."""
        self.mock_config.notion_data_source_id = None
        self.mock_client.databases.retrieve.return_value = {"data_sources": []}

        with self.assertRaises(ValueError):
            NotionClient()

    def test_init_raises_when_database_resolution_fails_unexpectedly(self):
        """Test initialization raises on unexpected database resolution failures."""
        self.mock_config.notion_data_source_id = None
        self.mock_client.databases.retrieve.side_effect = Exception("boom")

        with self.assertRaises(ValueError):
            NotionClient()

    def test_init_raises_when_database_payload_is_invalid(self):
        """Test initialization raises on malformed database payloads."""
        self.mock_config.notion_data_source_id = None
        self.mock_client.databases.retrieve.return_value = {"data_sources": [{}]}

        with self.assertRaises(ValueError):
            NotionClient()

    def test_check_page_exists_true(self):
        """Test check_page_exists when page exists."""
        # Setup mock
        self.mock_client.data_sources.query.return_value = {"results": [{"id": "page_id"}]}

        # Test
        result = self.notion_client.check_page_exists("Test Title")

        # Assert
        self.assertTrue(result)
        self.mock_client.data_sources.query.assert_called_once()

    def test_check_page_exists_false(self):
        """Test check_page_exists when page doesn't exist."""
        # Setup mock
        self.mock_client.data_sources.query.return_value = {"results": []}

        # Test
        result = self.notion_client.check_page_exists("Test Title")

        # Assert
        self.assertFalse(result)
        self.mock_client.data_sources.query.assert_called_once()

    def test_check_page_exists_error(self):
        """Test check_page_exists when an error occurs."""
        # Setup mock
        self.mock_client.data_sources.query.side_effect = MockAPIResponseError()

        # Test
        result = self.notion_client.check_page_exists("Test Title")

        # Assert
        self.assertIsNone(result)
        self.mock_client.data_sources.query.assert_called_once()
        self.mock_logger.error.assert_called_once()

    def test_check_page_exists_unexpected_error(self):
        """Test check_page_exists handles unexpected exceptions."""
        self.mock_client.data_sources.query.side_effect = Exception("boom")

        result = self.notion_client.check_page_exists("https://example.com")

        self.assertIsNone(result)
        self.mock_logger.error.assert_called_once()

    def test_add_text_chunks_to_page_single_chunk(self):
        """Test add_text_chunks_to_page with a single chunk."""
        # Test
        result = self.notion_client.add_text_chunks_to_page("page_id", "Short text")

        # Assert
        self.assertTrue(result)
        self.mock_client.blocks.children.append.assert_called_once()

    def test_add_text_chunks_to_page_multiple_chunks(self):
        """Test add_text_chunks_to_page with multiple chunks."""
        # Test with text larger than chunk size
        long_text = "a" * 3000
        result = self.notion_client.add_text_chunks_to_page("page_id", long_text)

        # Assert
        self.assertTrue(result)
        self.assertEqual(self.mock_client.blocks.children.append.call_count, 2)

    def test_add_text_chunks_to_page_error(self):
        """Test add_text_chunks_to_page when an error occurs."""
        # Setup mock
        self.mock_client.blocks.children.append.side_effect = MockAPIResponseError()

        # Test
        result = self.notion_client.add_text_chunks_to_page("page_id", "Test text")

        # Assert
        self.assertFalse(result)
        self.mock_client.blocks.children.append.assert_called_once()
        self.mock_logger.error.assert_called_once()

    def test_add_page_new_page(self):
        """Test add_page with a new page."""
        # Setup mocks
        with patch.object(self.notion_client, "check_page_exists", return_value=False):
            self.mock_client.pages.create.return_value = {"id": "new_page_id"}

            # Test
            result = self.notion_client.add_page("Test Title", "https://example.com", "Test Body", "2023-01-01")

            # Assert
            self.assertEqual(result, {"id": "new_page_id"})
            self.mock_client.pages.create.assert_called_once()
            self.assertEqual(
                self.mock_client.pages.create.call_args.kwargs["parent"],
                {"data_source_id": self.data_source_id},
            )
            self.mock_logger.info.assert_called()

    def test_add_page_existing_page(self):
        """Test add_page with an existing page."""
        # Setup mocks
        with patch.object(self.notion_client, "check_page_exists", return_value=True):
            # Test
            result = self.notion_client.add_page("Test Title", "https://example.com", "Test Body", "2023-01-01")

            # Assert
            self.assertIsNone(result)
            self.mock_client.pages.create.assert_not_called()
            self.mock_logger.info.assert_called_once()

    def test_add_page_duplicate_check_failure(self):
        """Test add_page aborts when the duplicate check fails."""
        with patch.object(self.notion_client, "check_page_exists", return_value=None):
            result = self.notion_client.add_page("Test Title", "https://example.com", "Test Body", "2023-01-01")

            self.assertIsNone(result)
            self.mock_client.pages.create.assert_not_called()
            self.mock_logger.error.assert_called_once()

    def test_add_page_body_append_failure(self):
        """Test add_page returns None when body chunks fail to append."""
        with patch.object(self.notion_client, "check_page_exists", return_value=False):
            with patch.object(self.notion_client, "add_text_chunks_to_page", return_value=False):
                self.mock_client.pages.create.return_value = {"id": "new_page_id"}

                result = self.notion_client.add_page("Test Title", "https://example.com", "Test Body", "2023-01-01")

                self.assertIsNone(result)
                self.mock_client.pages.create.assert_called_once()
                self.mock_logger.error.assert_called_once()

    def test_add_page_skips_pending_link(self):
        """Test add_page skips links already being created in this process."""
        with patch.object(self.notion_client, "_mark_link_pending", return_value=False):
            result = self.notion_client.add_page("Test Title", "https://example.com", "Test Body", "2023-01-01")

            self.assertIsNone(result)
            self.mock_client.pages.create.assert_not_called()
            self.mock_logger.info.assert_called_once()

    def test_add_page_error(self):
        """Test add_page when an error occurs."""
        # Setup mocks
        with patch.object(self.notion_client, "check_page_exists", return_value=False):
            self.mock_client.pages.create.side_effect = MockAPIResponseError()

            # Test
            result = self.notion_client.add_page("Test Title", "https://example.com", "Test Body", "2023-01-01")

            # Assert
            self.assertIsNone(result)
            self.mock_client.pages.create.assert_called_once()
            self.mock_logger.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()

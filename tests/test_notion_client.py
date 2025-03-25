"""Tests for the notion_client module."""

import unittest
from unittest.mock import patch, MagicMock
from src.feed_to_somewhere.notion_client import NotionClient
from notion_client.errors import APIResponseError


class TestNotionClient(unittest.TestCase):
    """Test cases for the NotionClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.token = "test_token"
        self.database_id = "test_database_id"

        # Create a patcher for the config
        self.config_patcher = patch("src.feed_to_somewhere.notion_client.config")
        self.mock_config = self.config_patcher.start()
        self.mock_config.notion_token = self.token
        self.mock_config.database_id = self.database_id
        self.mock_config.chunk_size = 2000

        # Create a patcher for the logger
        self.logger_patcher = patch("src.feed_to_somewhere.notion_client.logger")
        self.mock_logger = self.logger_patcher.start()

        # Create a patcher for the Client
        self.client_patcher = patch("src.feed_to_somewhere.notion_client.Client")
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
        self.assertEqual(self.notion_client.chunk_size, 2000)
        self.mock_client_class.assert_called_once_with(auth=self.token)

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        custom_token = "custom_token"
        custom_database_id = "custom_database_id"

        notion_client = NotionClient(token=custom_token, database_id=custom_database_id)

        self.assertEqual(notion_client.token, custom_token)
        self.assertEqual(notion_client.database_id, custom_database_id)
        self.mock_client_class.assert_called_with(auth=custom_token)

    def test_check_page_exists_true(self):
        """Test check_page_exists when page exists."""
        # Setup mock
        self.mock_client.databases.query.return_value = {"results": [{"id": "page_id"}]}

        # Test
        result = self.notion_client.check_page_exists("Test Title")

        # Assert
        self.assertTrue(result)
        self.mock_client.databases.query.assert_called_once()

    def test_check_page_exists_false(self):
        """Test check_page_exists when page doesn't exist."""
        # Setup mock
        self.mock_client.databases.query.return_value = {"results": []}

        # Test
        result = self.notion_client.check_page_exists("Test Title")

        # Assert
        self.assertFalse(result)
        self.mock_client.databases.query.assert_called_once()

    def test_check_page_exists_error(self):
        """Test check_page_exists when an error occurs."""
        # Setup mock
        mock_response = MagicMock()
        mock_error = APIResponseError(response=mock_response, message="Error message", code="error_code")
        self.mock_client.databases.query.side_effect = mock_error

        # Test
        result = self.notion_client.check_page_exists("Test Title")

        # Assert
        self.assertFalse(result)
        self.mock_client.databases.query.assert_called_once()
        self.mock_logger.error.assert_called_once()

    def test_add_text_chunks_to_page_single_chunk(self):
        """Test add_text_chunks_to_page with a single chunk."""
        # Test
        self.notion_client.add_text_chunks_to_page("page_id", "Short text")

        # Assert
        self.mock_client.blocks.children.append.assert_called_once()

    def test_add_text_chunks_to_page_multiple_chunks(self):
        """Test add_text_chunks_to_page with multiple chunks."""
        # Test with text larger than chunk size
        long_text = "a" * 3000
        self.notion_client.add_text_chunks_to_page("page_id", long_text)

        # Assert
        self.assertEqual(self.mock_client.blocks.children.append.call_count, 2)

    def test_add_text_chunks_to_page_error(self):
        """Test add_text_chunks_to_page when an error occurs."""
        # Setup mock
        mock_response = MagicMock()
        mock_error = APIResponseError(response=mock_response, message="Error message", code="error_code")
        self.mock_client.blocks.children.append.side_effect = mock_error

        # Test
        self.notion_client.add_text_chunks_to_page("page_id", "Test text")

        # Assert
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

    def test_add_page_error(self):
        """Test add_page when an error occurs."""
        # Setup mocks
        with patch.object(self.notion_client, "check_page_exists", return_value=False):
            mock_response = MagicMock()
            mock_error = APIResponseError(response=mock_response, message="Error message", code="error_code")
            self.mock_client.pages.create.side_effect = mock_error

            # Test
            result = self.notion_client.add_page("Test Title", "https://example.com", "Test Body", "2023-01-01")

            # Assert
            self.assertIsNone(result)
            self.mock_client.pages.create.assert_called_once()
            self.mock_logger.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()

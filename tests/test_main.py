"""Tests for the main module."""

import unittest
from unittest.mock import patch, MagicMock
import sys
from src.feed_to_somewhere.main import main, parse_args


class TestMain(unittest.TestCase):
    """Test cases for the main module."""

    def test_parse_args_defaults(self):
        """Test parse_args with default values."""
        # Mock config
        with patch("src.feed_to_somewhere.main.config") as mock_config:
            mock_config.feed_list_path = "feed_list.csv"
            
            # Test with no arguments
            args = parse_args([])
            
            # Assert
            self.assertEqual(args.feed_file, "feed_list.csv")
            self.assertEqual(args.max_workers, 10)
            self.assertEqual(args.log_level, "INFO")

    def test_parse_args_custom(self):
        """Test parse_args with custom values."""
        # Test with custom arguments
        args = parse_args(["--feed-file", "custom.csv", "--max-workers", "5", "--log-level", "DEBUG"])
        
        # Assert
        self.assertEqual(args.feed_file, "custom.csv")
        self.assertEqual(args.max_workers, 5)
        self.assertEqual(args.log_level, "DEBUG")

    @patch("src.feed_to_somewhere.main.setup_logger")
    @patch("src.feed_to_somewhere.main.NotionClient")
    @patch("src.feed_to_somewhere.main.FeedProcessor")
    def test_main_success(self, mock_processor_class, mock_notion_class, mock_setup_logger):
        """Test main function with successful processing."""
        # Mock processor
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_feeds.return_value = 5  # 5 feeds processed
        
        # Test
        exit_code = main(["--feed-file", "test.csv"])
        
        # Assert
        self.assertEqual(exit_code, 0)
        mock_setup_logger.assert_called_once()
        mock_notion_class.assert_called_once()
        mock_processor_class.assert_called_once()
        mock_processor.process_feeds.assert_called_once_with("test.csv")

    @patch("src.feed_to_somewhere.main.setup_logger")
    @patch("src.feed_to_somewhere.main.NotionClient")
    @patch("src.feed_to_somewhere.main.FeedProcessor")
    def test_main_no_feeds_processed(self, mock_processor_class, mock_notion_class, mock_setup_logger):
        """Test main function with no feeds processed."""
        # Mock processor
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_feeds.return_value = 0  # No feeds processed
        
        # Test
        exit_code = main(["--feed-file", "test.csv"])
        
        # Assert
        self.assertEqual(exit_code, 1)
        mock_setup_logger.assert_called_once()
        mock_notion_class.assert_called_once()
        mock_processor_class.assert_called_once()
        mock_processor.process_feeds.assert_called_once_with("test.csv")

    @patch("src.feed_to_somewhere.main.setup_logger")
    @patch("src.feed_to_somewhere.main.NotionClient")
    @patch("src.feed_to_somewhere.main.FeedProcessor")
    @patch("src.feed_to_somewhere.main.logger")
    def test_main_exception(self, mock_logger, mock_processor_class, mock_notion_class, mock_setup_logger):
        """Test main function with an exception."""
        # Mock processor to raise an exception
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_feeds.side_effect = Exception("Test error")
        
        # Test
        exit_code = main(["--feed-file", "test.csv"])
        
        # Assert
        self.assertEqual(exit_code, 1)
        mock_setup_logger.assert_called_once()
        mock_notion_class.assert_called_once()
        mock_processor_class.assert_called_once()
        mock_processor.process_feeds.assert_called_once_with("test.csv")
        mock_logger.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()

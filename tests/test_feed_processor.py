"""Tests for the feed_processor module."""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import sys
from src.feed_to_somewhere.feed_processor import FeedProcessor


class TestFeedProcessor(unittest.TestCase):
    """Test cases for the FeedProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a patcher for the logger
        self.logger_patcher = patch("src.feed_to_somewhere.feed_processor.logger")
        self.mock_logger = self.logger_patcher.start()
        
        # Create a patcher for the NotionClient
        self.notion_client_patcher = patch("src.feed_to_somewhere.feed_processor.NotionClient")
        self.mock_notion_client_class = self.notion_client_patcher.start()
        self.mock_notion_client = MagicMock()
        self.mock_notion_client_class.return_value = self.mock_notion_client
        
        # Create the FeedProcessor instance
        self.feed_processor = FeedProcessor()

    def tearDown(self):
        """Tear down test fixtures."""
        self.logger_patcher.stop()
        self.notion_client_patcher.stop()

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        self.assertEqual(self.feed_processor.notion_client, self.mock_notion_client)
        self.assertEqual(self.feed_processor.max_workers, 10)

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        custom_notion_client = MagicMock()
        custom_max_workers = 5
        
        feed_processor = FeedProcessor(
            notion_client=custom_notion_client,
            max_workers=custom_max_workers
        )
        
        self.assertEqual(feed_processor.notion_client, custom_notion_client)
        self.assertEqual(feed_processor.max_workers, custom_max_workers)

    def test_read_feed_urls_success(self):
        """Test read_feed_urls with a valid CSV file."""
        # Mock CSV content
        csv_content = "http://example.com/feed1\nhttp://example.com/feed2"
        
        # Mock open function
        with patch("builtins.open", mock_open(read_data=csv_content)):
            # Test
            urls = self.feed_processor.read_feed_urls("feed_list.csv")
            
            # Assert
            self.assertEqual(len(urls), 2)
            self.assertEqual(urls[0], "http://example.com/feed1")
            self.assertEqual(urls[1], "http://example.com/feed2")
            self.mock_logger.info.assert_called_once()

    def test_read_feed_urls_empty_file(self):
        """Test read_feed_urls with an empty CSV file."""
        # Mock open function
        with patch("builtins.open", mock_open(read_data="")):
            # Test
            urls = self.feed_processor.read_feed_urls("feed_list.csv")
            
            # Assert
            self.assertEqual(len(urls), 0)
            self.mock_logger.info.assert_called_once()

    def test_read_feed_urls_io_error(self):
        """Test read_feed_urls with an IO error."""
        # Mock open function to raise an IOError
        with patch("builtins.open", side_effect=IOError("File not found")):
            # Test
            urls = self.feed_processor.read_feed_urls("feed_list.csv")
            
            # Assert
            self.assertEqual(len(urls), 0)
            self.mock_logger.error.assert_called_once()

    @patch("src.feed_to_somewhere.feed_processor.feedparser.parse")
    def test_fetch_feed_entries_success(self, mock_parse):
        """Test fetch_feed_entries with a valid feed."""
        # Mock feedparser response
        mock_entry1 = MagicMock()
        mock_entry2 = MagicMock()
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry1, mock_entry2]
        mock_parse.return_value = mock_feed
        
        # Test
        entries = self.feed_processor.fetch_feed_entries("http://example.com/feed")
        
        # Assert
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0], mock_entry1)
        self.assertEqual(entries[1], mock_entry2)
        mock_parse.assert_called_once_with("http://example.com/feed")
        self.mock_logger.info.assert_called_once()

    @patch("src.feed_to_somewhere.feed_processor.feedparser.parse")
    def test_fetch_feed_entries_empty_feed(self, mock_parse):
        """Test fetch_feed_entries with an empty feed."""
        # Mock feedparser response
        mock_feed = MagicMock()
        mock_feed.entries = []
        mock_parse.return_value = mock_feed
        
        # Test
        entries = self.feed_processor.fetch_feed_entries("http://example.com/feed")
        
        # Assert
        self.assertEqual(len(entries), 0)
        mock_parse.assert_called_once_with("http://example.com/feed")
        self.mock_logger.info.assert_called_once()

    @patch("src.feed_to_somewhere.feed_processor.feedparser.parse")
    def test_fetch_feed_entries_error(self, mock_parse):
        """Test fetch_feed_entries with an error."""
        # Mock feedparser to raise an exception
        mock_parse.side_effect = Exception("Parse error")
        
        # Test
        entries = self.feed_processor.fetch_feed_entries("http://example.com/feed")
        
        # Assert
        self.assertEqual(len(entries), 0)
        mock_parse.assert_called_once_with("http://example.com/feed")
        self.mock_logger.error.assert_called_once()

    @patch("src.feed_to_somewhere.feed_processor.requests.get")
    @patch("src.feed_to_somewhere.feed_processor.BeautifulSoup")
    def test_extract_content_success(self, mock_bs, mock_get):
        """Test extract_content with a valid URL."""
        # Mock requests response
        mock_response = MagicMock()
        mock_get.return_value = mock_response
        
        # Mock BeautifulSoup
        mock_p1 = MagicMock()
        mock_p1.text = "Paragraph 1"
        mock_p2 = MagicMock()
        mock_p2.text = "Paragraph 2"
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = [mock_p1, mock_p2]
        mock_bs.return_value = mock_soup
        
        # Test
        content = self.feed_processor.extract_content("http://example.com/article")
        
        # Assert
        self.assertEqual(content, "Paragraph 1 Paragraph 2")
        mock_get.assert_called_once_with("http://example.com/article", timeout=30)
        mock_bs.assert_called_once()
        mock_soup.find_all.assert_called_once_with("p")

    @patch("src.feed_to_somewhere.feed_processor.requests.get")
    def test_extract_content_request_error(self, mock_get):
        """Test extract_content with a request error."""
        # Mock requests to raise an exception
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Connection error")
        
        # Test
        content = self.feed_processor.extract_content("http://example.com/article")
        
        # Assert
        self.assertEqual(content, "")
        mock_get.assert_called_once_with("http://example.com/article", timeout=30)
        self.mock_logger.error.assert_called_once()

    def test_process_entry_success(self):
        """Test process_entry with a valid entry."""
        # Mock entry
        mock_entry = {
            "title": "Test Title",
            "link": "http://example.com/article",
            "published_parsed": None
        }
        
        # Mock extract_content
        with patch.object(self.feed_processor, "extract_content", return_value="Test content"):
            # Mock add_page
            self.mock_notion_client.add_page.return_value = {"id": "page_id"}
            
            # Test
            result = self.feed_processor.process_entry(mock_entry, "2023-01-01")
            
            # Assert
            self.assertTrue(result)
            self.feed_processor.extract_content.assert_called_once_with("http://example.com/article")
            self.mock_notion_client.add_page.assert_called_once()

    def test_process_entry_no_link(self):
        """Test process_entry with an entry that has no link."""
        # Mock entry
        mock_entry = {
            "title": "Test Title",
            "link": "",
            "published_parsed": None
        }
        
        # Test
        result = self.feed_processor.process_entry(mock_entry, "2023-01-01")
        
        # Assert
        self.assertFalse(result)
        self.mock_logger.warning.assert_called_once()
        self.mock_notion_client.add_page.assert_not_called()

    def test_process_entry_extraction_failure(self):
        """Test process_entry when content extraction fails."""
        # Mock entry
        mock_entry = {
            "title": "Test Title",
            "link": "http://example.com/article",
            "published_parsed": None
        }
        
        # Mock extract_content to return empty string
        with patch.object(self.feed_processor, "extract_content", return_value=""):
            # Mock add_page
            self.mock_notion_client.add_page.return_value = {"id": "page_id"}
            
            # Test
            result = self.feed_processor.process_entry(mock_entry, "2023-01-01")
            
            # Assert
            self.assertTrue(result)
            self.feed_processor.extract_content.assert_called_once_with("http://example.com/article")
            self.mock_logger.warning.assert_called_once()
            self.mock_notion_client.add_page.assert_called_once()

    def test_process_entry_notion_failure(self):
        """Test process_entry when adding to Notion fails."""
        # Mock entry
        mock_entry = {
            "title": "Test Title",
            "link": "http://example.com/article",
            "published_parsed": None
        }
        
        # Mock extract_content
        with patch.object(self.feed_processor, "extract_content", return_value="Test content"):
            # Mock add_page to return None (failure)
            self.mock_notion_client.add_page.return_value = None
            
            # Test
            result = self.feed_processor.process_entry(mock_entry, "2023-01-01")
            
            # Assert
            self.assertFalse(result)
            self.feed_processor.extract_content.assert_called_once_with("http://example.com/article")
            self.mock_notion_client.add_page.assert_called_once()

    @patch("src.feed_to_somewhere.feed_processor.concurrent.futures.ThreadPoolExecutor")
    def test_process_feed_success(self, mock_executor_class):
        """Test process_feed with a valid feed."""
        # Mock fetch_feed_entries
        mock_entry1 = {"title": "Entry 1", "link": "http://example.com/article1"}
        mock_entry2 = {"title": "Entry 2", "link": "http://example.com/article2"}
        
        with patch.object(self.feed_processor, "fetch_feed_entries", return_value=[mock_entry1, mock_entry2]):
            # Mock ThreadPoolExecutor
            mock_executor = MagicMock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor
            
            # Mock submit and result
            mock_future1 = MagicMock()
            mock_future1.result.return_value = True
            mock_future2 = MagicMock()
            mock_future2.result.return_value = False
            
            mock_executor.submit.side_effect = [mock_future1, mock_future2]
            
            # Mock as_completed to return futures in order
            with patch("src.feed_to_somewhere.feed_processor.concurrent.futures.as_completed", 
                      return_value=[mock_future1, mock_future2]):
                
                # Test
                result = self.feed_processor.process_feed("http://example.com/feed")
                
                # Assert
                self.assertEqual(result, 1)  # One successful entry
                self.feed_processor.fetch_feed_entries.assert_called_once_with("http://example.com/feed")
                self.assertEqual(mock_executor.submit.call_count, 2)
                self.mock_logger.info.assert_called()

    def test_process_feed_no_entries(self):
        """Test process_feed with a feed that has no entries."""
        # Mock fetch_feed_entries to return empty list
        with patch.object(self.feed_processor, "fetch_feed_entries", return_value=[]):
            # Test
            result = self.feed_processor.process_feed("http://example.com/feed")
            
            # Assert
            self.assertEqual(result, 0)
            self.feed_processor.fetch_feed_entries.assert_called_once_with("http://example.com/feed")

    @patch("src.feed_to_somewhere.feed_processor.concurrent.futures.ThreadPoolExecutor")
    def test_process_feeds_success(self, mock_executor_class):
        """Test process_feeds with valid feeds."""
        # Mock read_feed_urls
        with patch.object(self.feed_processor, "read_feed_urls", 
                         return_value=["http://example.com/feed1", "http://example.com/feed2"]):
            
            # Mock ThreadPoolExecutor
            mock_executor = MagicMock()
            mock_executor_class.return_value.__enter__.return_value = mock_executor
            
            # Mock submit and result
            mock_future1 = MagicMock()
            mock_future1.result.return_value = 2  # 2 entries processed
            mock_future2 = MagicMock()
            mock_future2.result.return_value = 0  # 0 entries processed
            
            mock_executor.submit.side_effect = [mock_future1, mock_future2]
            
            # Mock as_completed to return futures in order
            with patch("src.feed_to_somewhere.feed_processor.concurrent.futures.as_completed", 
                      return_value=[mock_future1, mock_future2]):
                
                # Test
                result = self.feed_processor.process_feeds("feed_list.csv")
                
                # Assert
                self.assertEqual(result, 1)  # One successful feed
                self.feed_processor.read_feed_urls.assert_called_once_with("feed_list.csv")
                self.assertEqual(mock_executor.submit.call_count, 2)
                self.mock_logger.info.assert_called()

    def test_process_feeds_no_urls(self):
        """Test process_feeds with no feed URLs."""
        # Mock read_feed_urls to return empty list
        with patch.object(self.feed_processor, "read_feed_urls", return_value=[]):
            # Test
            result = self.feed_processor.process_feeds("feed_list.csv")
            
            # Assert
            self.assertEqual(result, 0)
            self.feed_processor.read_feed_urls.assert_called_once_with("feed_list.csv")
            self.mock_logger.warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()

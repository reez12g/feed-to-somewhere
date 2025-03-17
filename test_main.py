import unittest
from unittest.mock import patch, MagicMock
import pytest
import main
import re
import io
import sys
from datetime import datetime
from notion_client.errors import APIResponseError

class TestMain(unittest.TestCase):
    
    def test_clean_text(self):
        # Test with normal text
        text = "Hello, World!"
        self.assertEqual(main.clean_text(text), text)
        
        # Test with invalid unicode characters
        text_with_invalid = "Hello\uD800World"
        self.assertEqual(main.clean_text(text_with_invalid), "HelloWorld")
    
    @patch('main.notion')
    def test_check_page_exists_true(self, mock_notion):
        # Setup mock
        mock_response = {"results": [{"id": "page_id"}]}
        mock_notion.databases.query.return_value = mock_response
        
        # Test
        result = main.check_page_exists("Test Title")
        
        # Assert
        self.assertTrue(result)
        mock_notion.databases.query.assert_called_once()
    
    @patch('main.notion')
    def test_check_page_exists_false(self, mock_notion):
        # Setup mock
        mock_response = {"results": []}
        mock_notion.databases.query.return_value = mock_response
        
        # Test
        result = main.check_page_exists("Test Title")
        
        # Assert
        self.assertFalse(result)
        mock_notion.databases.query.assert_called_once()
    
    @patch('main.notion')
    def test_add_text_chunks_to_page(self, mock_notion):
        # Test with text smaller than chunk size
        main.add_text_chunks_to_page("page_id", "Short text", 2000)
        mock_notion.blocks.children.append.assert_called_once()
        
        # Reset mock
        mock_notion.blocks.children.append.reset_mock()
        
        # Test with text larger than chunk size
        long_text = "a" * 3000
        main.add_text_chunks_to_page("page_id", long_text, 2000)
        self.assertEqual(mock_notion.blocks.children.append.call_count, 2)
    
    @patch('main.notion')
    @patch('main.check_page_exists')
    def test_add_to_notion_new_page(self, mock_check_page_exists, mock_notion):
        # Setup mocks
        mock_check_page_exists.return_value = False
        mock_notion.pages.create.return_value = {"id": "new_page_id"}
        
        # Test
        main.add_to_notion("Test Title", "https://example.com", "Test Body", "2023-01-01")
        
        # Assert
        mock_notion.pages.create.assert_called_once()
        mock_notion.blocks.children.append.assert_called_once()
    
    @patch('main.notion')
    @patch('main.check_page_exists')
    def test_add_to_notion_existing_page(self, mock_check_page_exists, mock_notion):
        # Setup mocks
        mock_check_page_exists.return_value = True
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Test
        main.add_to_notion("Test Title", "https://example.com", "Test Body", "2023-01-01")
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        
        # Assert
        mock_notion.pages.create.assert_not_called()
        self.assertIn("already exists", captured_output.getvalue())
    
    @patch('main.notion')
    @patch('main.check_page_exists')
    def test_add_to_notion_api_error(self, mock_check_page_exists, mock_notion):
        # Setup mocks
        mock_check_page_exists.return_value = False
        mock_response = MagicMock()
        # Create a mock error with the required parameters
        mock_error = APIResponseError(response=mock_response, message="Error message", code="error_code")
        mock_notion.pages.create.side_effect = mock_error
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Test
        main.add_to_notion("Test Title", "https://example.com", "Test Body", "2023-01-01")
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        
        # Assert
        self.assertIn("Failed to add page", captured_output.getvalue())
    
    @patch('main.Thread')
    @patch('csv.reader')
    def test_fetch_and_process_feeds(self, mock_csv_reader, mock_thread):
        # Setup mocks
        mock_feed = MagicMock()
        mock_feed_list = [["http://example.com/feed"]]
        mock_csv_reader.return_value = mock_feed_list
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Mock open file
        mock_open = unittest.mock.mock_open()
        with patch('builtins.open', mock_open):
            main.fetch_and_process_feeds("feed_list.csv")
        
        # Assert
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        mock_thread_instance.join.assert_called_once()
    
    @patch('main.Thread')
    @patch('main.feedparser.parse')
    @patch('main.requests.get')
    @patch('main.BeautifulSoup')
    def test_process_feed(self, mock_bs, mock_requests_get, mock_feedparser_parse, mock_thread):
        # Setup mocks
        mock_entry = MagicMock()
        mock_entry.title = "Test Entry"
        mock_entry.link = "https://example.com/entry"
        
        # Create a structured time object instead of a MagicMock
        class PublishedTime:
            tm_year = 2023
            tm_mon = 1
            tm_mday = 1
            
        published_time = PublishedTime()
        # Use get method that returns the structured time
        mock_entry.get = lambda key, default=None: published_time if key == "published_parsed" else default
        
        mock_feed = MagicMock()
        mock_feed.entries = [mock_entry]
        mock_feedparser_parse.return_value = mock_feed
        
        mock_response = MagicMock()
        mock_requests_get.return_value = mock_response
        
        mock_soup = MagicMock()
        mock_p = MagicMock()
        mock_p.text = "Test paragraph"
        mock_soup.find_all.return_value = [mock_p]
        mock_bs.return_value = mock_soup
        
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Test
        main.process_feed("http://example.com/feed", "2023-01-01")
        
        # Assert
        mock_feedparser_parse.assert_called_once()
        mock_requests_get.assert_called_once()
        mock_bs.assert_called_once()
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        mock_thread_instance.join.assert_called_once()

if __name__ == '__main__':
    unittest.main() 
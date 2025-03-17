import pytest
import main
import io
import sys
from unittest.mock import patch, MagicMock
from notion_client.errors import APIResponseError


def test_clean_text():
    """Test the clean_text function with normal and invalid Unicode text."""
    # Test normal text
    text = "Hello, World!"
    assert main.clean_text(text) == text
    
    # Test with invalid Unicode characters
    text_with_invalid = "Hello\uD800World"
    assert main.clean_text(text_with_invalid) == "HelloWorld"


def test_check_page_exists_true(mock_notion_client):
    """Test check_page_exists when page exists."""
    # Setup mock
    mock_notion_client.databases.query.return_value = {"results": [{"id": "page_id"}]}
    
    # Test
    result = main.check_page_exists("Test Title")
    
    # Assert
    assert result is True
    mock_notion_client.databases.query.assert_called_once()


def test_check_page_exists_false(mock_notion_client):
    """Test check_page_exists when page doesn't exist."""
    # Setup mock
    mock_notion_client.databases.query.return_value = {"results": []}
    
    # Test
    result = main.check_page_exists("Test Title")
    
    # Assert
    assert result is False
    mock_notion_client.databases.query.assert_called_once()


def test_add_text_chunks_to_page(mock_notion_client):
    """Test adding text chunks to a page."""
    # Test with short text
    main.add_text_chunks_to_page("page_id", "Short text", 2000)
    mock_notion_client.blocks.children.append.assert_called_once()
    
    # Reset mock
    mock_notion_client.blocks.children.append.reset_mock()
    
    # Test with long text (requiring multiple chunks)
    long_text = "a" * 3000
    main.add_text_chunks_to_page("page_id", long_text, 2000)
    assert mock_notion_client.blocks.children.append.call_count == 2


def test_add_to_notion_new_page(mock_notion_client):
    """Test adding a new page to Notion."""
    # Setup mocks
    with patch('main.check_page_exists', return_value=False):
        mock_notion_client.pages.create.return_value = {"id": "new_page_id"}
        
        # Test
        main.add_to_notion("Test Title", "https://example.com", "Test Body", "2023-01-01")
        
        # Assert
        mock_notion_client.pages.create.assert_called_once()
        mock_notion_client.blocks.children.append.assert_called_once()


def test_add_to_notion_existing_page(mock_notion_client):
    """Test adding a page that already exists in Notion."""
    # Setup mocks
    with patch('main.check_page_exists', return_value=True):
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Test
        main.add_to_notion("Test Title", "https://example.com", "Test Body", "2023-01-01")
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        
        # Assert
        mock_notion_client.pages.create.assert_not_called()
        assert "already exists" in captured_output.getvalue()


def test_add_to_notion_api_error(mock_notion_client):
    """Test handling API errors when adding to Notion."""
    # Setup mocks
    with patch('main.check_page_exists', return_value=False):
        mock_response = MagicMock()
        # Create a mock error with required parameters
        mock_error = APIResponseError(response=mock_response, message="Error message", code="error_code")
        mock_notion_client.pages.create.side_effect = mock_error
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Test
        main.add_to_notion("Test Title", "https://example.com", "Test Body", "2023-01-01")
        
        # Reset stdout
        sys.stdout = sys.__stdout__
        
        # Assert
        assert "Failed to add page" in captured_output.getvalue()


def test_fetch_and_process_feeds(mock_thread):
    """Test fetching and processing feeds from CSV."""
    mock_thread_obj, mock_thread_instance = mock_thread
    
    # Setup mock for CSV reader
    mock_feed_list = [["http://example.com/feed"]]
    with patch('csv.reader', return_value=mock_feed_list):
        # Mock open file
        with patch('builtins.open', MagicMock()):
            # Test
            main.fetch_and_process_feeds("feed_list.csv")
    
    # Assert
    mock_thread_obj.assert_called_once()
    mock_thread_instance.start.assert_called_once()
    mock_thread_instance.join.assert_called_once()


def test_process_feed(mock_feedparser, mock_requests, mock_bs4, mock_thread):
    """Test processing a single feed."""
    mock_thread_obj, mock_thread_instance = mock_thread
    
    # Setup mock for feedparser
    mock_entry = MagicMock()
    mock_entry.title = "Test Entry"
    mock_entry.link = "https://example.com/entry"
    
    # Create a structured time object instead of using MagicMock
    class PublishedParsed:
        tm_year = 2023
        tm_mon = 1
        tm_mday = 1
    
    published_time = PublishedParsed()
    # Use get method that returns the structured time 
    mock_entry.get = lambda key, default=None: published_time if key == "published_parsed" else default
    
    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_feedparser.parse.return_value = mock_feed
    
    # Setup mock for requests
    mock_response = MagicMock()
    mock_requests.get.return_value = mock_response
    
    # Setup mock for BeautifulSoup
    mock_soup = MagicMock()
    mock_p = MagicMock()
    mock_p.text = "Test paragraph"
    mock_soup.find_all.return_value = [mock_p]
    mock_bs4.return_value = mock_soup
    
    # Test
    main.process_feed("http://example.com/feed", "2023-01-01")
    
    # Assert
    mock_feedparser.parse.assert_called_once()
    mock_requests.get.assert_called_once()
    mock_bs4.assert_called_once()
    mock_thread_obj.assert_called_once()
    mock_thread_instance.start.assert_called_once()
    mock_thread_instance.join.assert_called_once()


def test_process_feed_missing_date(mock_feedparser, mock_requests, mock_bs4, mock_thread):
    """Test processing a feed entry with missing date."""
    mock_thread_obj, mock_thread_instance = mock_thread
    
    # Setup mock for feedparser
    mock_entry = MagicMock()
    mock_entry.title = "Test Entry"
    mock_entry.link = "https://example.com/entry"
    
    # No published_parsed attribute
    mock_entry.get = lambda x: None
    
    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_feedparser.parse.return_value = mock_feed
    
    # Setup mock for requests
    mock_response = MagicMock()
    mock_requests.get.return_value = mock_response
    
    # Setup mock for BeautifulSoup
    mock_soup = MagicMock()
    mock_p = MagicMock()
    mock_p.text = "Test paragraph"
    mock_soup.find_all.return_value = [mock_p]
    mock_bs4.return_value = mock_soup
    
    # Test
    current_date = "2023-01-01"
    main.process_feed("http://example.com/feed", current_date)
    
    # The test passes if no exception is raised and the thread is started
    mock_thread_obj.assert_called_once()
    mock_thread_instance.start.assert_called_once() 
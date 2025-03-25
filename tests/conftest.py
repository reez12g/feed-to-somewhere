"""Pytest fixtures for Feed to Somewhere tests."""

import pytest
from unittest.mock import patch, MagicMock
from notion_client.errors import APIResponseError


@pytest.fixture
def mock_notion_client():
    """Fixture to mock the Notion client."""
    with patch('src.feed_to_somewhere.notion_client.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_feedparser():
    """Fixture to mock feedparser."""
    with patch('src.feed_to_somewhere.feed_processor.feedparser') as mock_feedparser:
        yield mock_feedparser


@pytest.fixture
def mock_requests():
    """Fixture to mock requests."""
    with patch('src.feed_to_somewhere.feed_processor.requests') as mock_requests:
        yield mock_requests


@pytest.fixture
def mock_bs4():
    """Fixture to mock BeautifulSoup."""
    with patch('src.feed_to_somewhere.feed_processor.BeautifulSoup') as mock_bs:
        yield mock_bs


@pytest.fixture
def mock_thread_pool():
    """Fixture to mock ThreadPoolExecutor."""
    with patch('src.feed_to_somewhere.feed_processor.concurrent.futures.ThreadPoolExecutor') as mock_executor_class:
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Create mock futures
        mock_future = MagicMock()
        mock_future.result.return_value = True
        mock_executor.submit.return_value = mock_future
        
        # Mock as_completed to return the mock future
        with patch('src.feed_to_somewhere.feed_processor.concurrent.futures.as_completed', 
                  return_value=[mock_future]):
            yield mock_executor_class, mock_executor, mock_future


@pytest.fixture
def mock_config():
    """Fixture to mock config."""
    with patch('src.feed_to_somewhere.config.config') as mock_config:
        mock_config.notion_token = "test_token"
        mock_config.database_id = "test_database_id"
        mock_config.feed_list_path = "feed_list.csv"
        mock_config.chunk_size = 2000
        yield mock_config


@pytest.fixture
def mock_logger():
    """Fixture to mock logger."""
    with patch('src.feed_to_somewhere.logger.logger') as mock_logger:
        yield mock_logger

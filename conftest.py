import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_notion_client():
    """Fixture to mock the Notion client."""
    with patch('main.notion') as mock_notion:
        yield mock_notion


@pytest.fixture
def mock_feedparser():
    """Fixture to mock feedparser."""
    with patch('main.feedparser') as mock_feedparser:
        yield mock_feedparser


@pytest.fixture
def mock_requests():
    """Fixture to mock requests."""
    with patch('main.requests') as mock_requests:
        yield mock_requests


@pytest.fixture
def mock_bs4():
    """Fixture to mock BeautifulSoup."""
    with patch('main.BeautifulSoup') as mock_bs:
        yield mock_bs


@pytest.fixture
def mock_thread():
    """Fixture to mock Thread."""
    with patch('main.Thread') as mock_thread:
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        yield mock_thread, mock_thread_instance

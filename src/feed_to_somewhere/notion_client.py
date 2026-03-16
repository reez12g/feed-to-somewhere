"""Notion API client for Feed to Somewhere."""

import threading
from typing import Any, Dict, Optional, Set
from notion_client import Client
from notion_client.errors import APIResponseError

from .config import config, require
from .logger import logger
from .utils import chunk_text


class NotionClient:
    """Client for interacting with the Notion API."""

    def __init__(self, token: Optional[str] = None, database_id: Optional[str] = None):
        """
        Initialize the Notion client.

        Args:
            token: Notion API token. If None, uses the token from config.
            database_id: Notion database ID. If None, uses the database_id from config.
        """
        self.token = require(token or config.notion_token, "NOTION_API_KEY")
        self.database_id = require(database_id or config.database_id, "NOTION_DATABASE_ID")
        self.client = Client(auth=self.token)
        self.chunk_size = config.chunk_size
        self._pending_links: Set[str] = set()
        self._pending_links_lock = threading.Lock()

    def _mark_link_pending(self, link: str) -> bool:
        """
        Track links currently being created to avoid duplicate writes in this process.

        Args:
            link: The page URL.

        Returns:
            True when the link was marked, False when it is already pending.
        """
        with self._pending_links_lock:
            if link in self._pending_links:
                return False

            self._pending_links.add(link)
            return True

    def _clear_pending_link(self, link: str) -> None:
        """Release a link previously marked as pending."""
        with self._pending_links_lock:
            self._pending_links.discard(link)

    def check_page_exists(self, link: str) -> Optional[bool]:
        """
        Check if a page with the specified URL exists in the database.

        Args:
            link: The URL to check.

        Returns:
            True if the page exists, False if it does not, or None if the
            existence check failed.
        """
        try:
            query = self.client.databases.query(
                database_id=self.database_id,
                filter={"property": "URL", "url": {"equals": link}}
            )
            return len(query.get("results", [])) > 0
        except APIResponseError as e:
            logger.error(f"Failed to check if page exists: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error checking if page exists: {e}")
            return None

    def add_text_chunks_to_page(self, page_id: str, text: str) -> bool:
        """
        Add text to a page by dividing it into chunks.

        Args:
            page_id: The ID of the page to add text to.
            text: The text to add.

        Returns:
            True if all chunks were added, False otherwise.
        """
        chunks = chunk_text(text, self.chunk_size)

        for chunk in chunks:
            try:
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=[
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": chunk}}]
                            },
                        }
                    ],
                )
            except APIResponseError as e:
                logger.error(f"Failed to add text chunk to page: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error adding text chunk to page: {e}")
                return False

        return True

    def add_page(self, title: str, link: str, body: str, date: str) -> Optional[Dict[str, Any]]:
        """
        Add a new page to Notion. Skip if it already exists.

        Args:
            title: The title of the page.
            link: The URL to associate with the page.
            body: The content of the page.
            date: The date to associate with the page in ISO format (YYYY-MM-DD).

        Returns:
            The created page data if successful, None otherwise.
        """
        if not self._mark_link_pending(link):
            logger.info(f"Page for URL '{link}' is already being created.")
            return None

        try:
            page_exists = self.check_page_exists(link)
            if page_exists is None:
                logger.error(f"Skipping page '{title}' because the duplicate check failed.")
                return None

            if page_exists:
                logger.info(f"Page for URL '{link}' already exists.")
                return None

            new_page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Name": {"title": [{"text": {"content": title}}]},
                    "URL": {"url": link},
                    "Date": {"date": {"start": date}},
                },
            )

            if not self.add_text_chunks_to_page(new_page["id"], body):
                logger.error(f"Failed to add body content for page '{title}'")
                return None

            logger.info(f"Added page '{title}'")
            return new_page

        except APIResponseError as e:
            logger.error(f"Failed to add page '{title}'. Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error adding page '{title}': {e}")
            return None
        finally:
            self._clear_pending_link(link)

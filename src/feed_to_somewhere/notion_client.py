"""Notion API client for Feed to Somewhere."""

from typing import Dict, List, Any, Optional
from notion_client import Client
from notion_client.errors import APIResponseError

from .config import config
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
        self.token = token or config.notion_token
        self.database_id = database_id or config.database_id
        self.client = Client(auth=self.token)
        self.chunk_size = config.chunk_size

    def check_page_exists(self, title: str) -> bool:
        """
        Check if a page with the specified title exists in the database.

        Args:
            title: The title to check.

        Returns:
            True if the page exists, False otherwise.
        """
        try:
            query = self.client.databases.query(
                database_id=self.database_id,
                filter={"property": "Name", "title": {"equals": title}}
            )
            return len(query["results"]) > 0
        except APIResponseError as e:
            logger.error(f"Failed to check if page exists: {e}")
            return False

    def add_text_chunks_to_page(self, page_id: str, text: str) -> None:
        """
        Add text to a page by dividing it into chunks.

        Args:
            page_id: The ID of the page to add text to.
            text: The text to add.
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
        try:
            if self.check_page_exists(title):
                logger.info(f"Page '{title}' already exists.")
                return None

            new_page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Name": {"title": [{"text": {"content": title}}]},
                    "URL": {"url": link},
                    "Date": {"date": {"start": date}},
                },
            )
            
            self.add_text_chunks_to_page(new_page["id"], body)
            logger.info(f"Added page '{title}'")
            return new_page
            
        except APIResponseError as e:
            logger.error(f"Failed to add page '{title}'. Error: {e}")
            return None

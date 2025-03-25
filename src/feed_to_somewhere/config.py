"""Configuration module for Feed to Somewhere."""

import os
from typing import Optional


class Config:
    """Configuration class for the application."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.notion_token: str = self._get_required_env("NOTION_API_KEY")
        self.database_id: str = self._get_required_env("NOTION_DATABASE_ID")
        self.feed_list_path: str = os.getenv("FEED_LIST_PATH", "feed_list.csv")
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "2000"))

    @staticmethod
    def _get_required_env(name: str) -> str:
        """
        Get a required environment variable.

        Args:
            name: The name of the environment variable.

        Returns:
            The value of the environment variable.

        Raises:
            ValueError: If the environment variable is not set.
        """
        value = os.getenv(name)
        if value is None:
            raise ValueError(f"Environment variable {name} is required")
        return value


# Create a singleton instance
config = Config()

"""Configuration module for Feed to Somewhere."""

import os
from typing import Optional
from pathlib import Path

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    # Look for .env file in the project root
    env_path = Path(__file__).resolve().parents[2] / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv is not installed, continue without it
    pass


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

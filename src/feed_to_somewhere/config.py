"""Configuration module for Feed to Somewhere."""

import os
from pathlib import Path
from typing import Optional


def _load_dotenv() -> None:
    """Load a project-local ``.env`` file when python-dotenv is available."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(dotenv_path=env_path)


class Config:
    """Configuration class for the application."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.notion_token: Optional[str] = os.getenv("NOTION_API_KEY")
        self.database_id: Optional[str] = os.getenv("NOTION_DATABASE_ID")
        self.feed_list_path: str = os.getenv("FEED_LIST_PATH", "feed_list.csv")
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "2000"))

_load_dotenv()


def require(value: Optional[str], name: str) -> str:
    """
    Validate that a required setting is present.

    Args:
        value: The resolved setting value.
        name: The environment variable name to mention in the error.

    Returns:
        The validated value.

    Raises:
        ValueError: If the value is missing.
    """
    if value:
        return value
    raise ValueError(f"Environment variable {name} is required")


config = Config()

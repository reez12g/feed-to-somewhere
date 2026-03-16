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
        self._chunk_size: str = os.getenv("CHUNK_SIZE", "2000")

    @property
    def chunk_size(self) -> int:
        """Return the validated Notion block chunk size."""
        return require_positive_int(self._chunk_size, "CHUNK_SIZE")

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


def require_positive_int(value: str, name: str) -> int:
    """
    Validate that a setting resolves to a positive integer.

    Args:
        value: The raw setting value.
        name: The setting name to mention in the error.

    Returns:
        The validated integer.

    Raises:
        ValueError: If the value cannot be parsed or is not positive.
    """
    try:
        parsed_value = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Environment variable {name} must be a positive integer") from exc

    if parsed_value <= 0:
        raise ValueError(f"Environment variable {name} must be a positive integer")

    return parsed_value


config = Config()

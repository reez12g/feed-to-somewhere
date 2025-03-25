"""Utility functions for Feed to Somewhere."""

import re
from typing import List, Optional
from datetime import datetime


def clean_text(text: str) -> str:
    """
    Remove invalid Unicode characters from text.

    Args:
        text: The text to clean.

    Returns:
        The cleaned text.
    """
    return re.sub(r"[^\u0000-\uD7FF\uE000-\uFFFF]", "", text)


def format_date(date_struct: Optional[object], default_date: str) -> str:
    """
    Format a date structure into ISO format string.

    Args:
        date_struct: A time structure object with tm_year, tm_mon, and tm_mday attributes.
        default_date: Default date string to use if date_struct is None.

    Returns:
        A formatted date string in ISO format (YYYY-MM-DD).
    """
    if not date_struct:
        return default_date

    try:
        return f"{date_struct.tm_year}-{date_struct.tm_mon:02d}-{date_struct.tm_mday:02d}"
    except (AttributeError, TypeError):
        return default_date


def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """
    Split text into chunks of specified size.

    Args:
        text: The text to split.
        chunk_size: Maximum size of each chunk.

    Returns:
        A list of text chunks.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def get_current_date_iso() -> str:
    """
    Get the current date in ISO format.

    Returns:
        Current date in ISO format (YYYY-MM-DD).
    """
    return datetime.now().date().isoformat()

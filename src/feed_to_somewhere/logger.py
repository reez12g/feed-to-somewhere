"""Logging configuration for Feed to Somewhere."""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "feed_to_somewhere", level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        name: The name of the logger.
        level: The logging level.

    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler if not already added
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger


# Create a default logger instance
logger = setup_logger()

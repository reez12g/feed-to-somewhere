"""Logging configuration for Feed to Somewhere."""

import logging
import sys


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
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create console handler if not already added
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
    else:
        handler = logger.handlers[0]

    handler.setLevel(level)
    handler.setFormatter(formatter)
    return logger


# Create a default logger instance
logger = setup_logger()

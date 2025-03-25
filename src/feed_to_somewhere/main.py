"""Main entry point for Feed to Somewhere."""

import sys
import argparse
from typing import List, Optional

from .config import config
from .logger import logger, setup_logger
from .notion_client import NotionClient
from .feed_processor import FeedProcessor


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.

    Args:
        args: Command line arguments. If None, sys.argv is used.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Feed to Somewhere - Process RSS feeds and save to Notion")

    parser.add_argument(
        "--feed-file",
        type=str,
        default=config.feed_list_path,
        help=f"Path to CSV file containing feed URLs (default: {config.feed_list_path})"
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        default=10,
        help="Maximum number of worker threads (default: 10)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the application.

    Args:
        args: Command line arguments. If None, sys.argv is used.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parsed_args = parse_args(args)

    # Set up logging with the specified level
    log_level = getattr(sys.modules["logging"], parsed_args.log_level)
    setup_logger(level=log_level)

    try:
        # Initialize the Notion client
        notion_client = NotionClient()

        # Initialize the feed processor
        processor = FeedProcessor(
            notion_client=notion_client,
            max_workers=parsed_args.max_workers
        )

        # Process feeds
        success_count = processor.process_feeds(parsed_args.feed_file)

        if success_count > 0:
            logger.info(f"Successfully processed {success_count} feeds")
            return 0
        else:
            logger.warning("No feeds were successfully processed")
            return 1

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

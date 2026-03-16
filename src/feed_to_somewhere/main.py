"""Main entry point for Feed to Somewhere."""

import sys
import argparse
from typing import List, Optional

from . import __version__
from .config import config
from .logger import logger, setup_logger
from .notion_client import NotionClient
from .feed_processor import FeedProcessor


def positive_int(value: str) -> int:
    """Parse an argparse integer value and reject non-positive inputs."""
    parsed_value = int(value)
    if parsed_value <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed_value


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
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--feed-file",
        type=str,
        default=config.feed_list_path,
        help=f"Path to CSV file containing feed URLs (default: {config.feed_list_path})"
    )

    parser.add_argument(
        "--feed-url",
        action="append",
        dest="feed_urls",
        default=[],
        help="Process a single feed URL directly. Can be specified multiple times."
    )

    parser.add_argument(
        "--max-workers",
        type=positive_int,
        default=10,
        help="Maximum number of worker threads (default: 10)"
    )

    parser.add_argument(
        "--max-feeds",
        type=positive_int,
        default=None,
        help="Process at most this many feeds"
    )

    parser.add_argument(
        "--max-entries",
        type=positive_int,
        default=None,
        help="Process at most this many entries per feed"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate feeds and log what would be processed without writing to Notion"
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
        if parsed_args.feed_urls:
            logger.info(f"Processing {len(parsed_args.feed_urls)} feed URLs provided on the command line")

        if parsed_args.dry_run:
            logger.info("Running in dry-run mode; Notion will not be modified")

        # Initialize the Notion client only when writes are enabled.
        notion_client = None if parsed_args.dry_run else NotionClient()

        # Initialize the feed processor
        processor = FeedProcessor(
            notion_client=notion_client,
            max_workers=parsed_args.max_workers,
            dry_run=parsed_args.dry_run,
            max_entries_per_feed=parsed_args.max_entries,
        )

        # Process feeds
        if parsed_args.feed_urls:
            success_count = processor.process_feed_urls(parsed_args.feed_urls, max_feeds=parsed_args.max_feeds)
        else:
            success_count = processor.process_feeds(parsed_args.feed_file, max_feeds=parsed_args.max_feeds)

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

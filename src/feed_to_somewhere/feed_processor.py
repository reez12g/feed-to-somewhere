"""Feed processing module for Feed to Somewhere."""

import csv
import concurrent.futures
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from .logger import logger
from .utils import clean_text, format_date, get_current_date_iso
from .notion_client import NotionClient


class FeedProcessor:
    """Processor for RSS feeds."""

    ARTICLE_REQUEST_HEADERS = {"User-Agent": "feed-to-somewhere/0.1.0"}

    def __init__(
        self,
        notion_client: Optional[NotionClient] = None,
        max_workers: int = 10,
        dry_run: bool = False,
        max_entries_per_feed: Optional[int] = None,
    ):
        """
        Initialize the feed processor.

        Args:
            notion_client: The Notion client to use. If None, a new client is created.
            max_workers: Maximum number of worker threads to use.
            dry_run: Whether to log planned work without writing to Notion.
            max_entries_per_feed: Optional per-feed entry limit.
        """
        if max_workers <= 0:
            raise ValueError("max_workers must be a positive integer")

        if max_entries_per_feed is not None and max_entries_per_feed <= 0:
            raise ValueError("max_entries_per_feed must be a positive integer")

        self.notion_client = notion_client
        self.max_workers = max_workers
        self.dry_run = dry_run
        self.max_entries_per_feed = max_entries_per_feed

        if not self.dry_run and self.notion_client is None:
            self.notion_client = NotionClient()

    @staticmethod
    def is_supported_url(url: str) -> bool:
        """
        Validate that a URL uses http(s) and includes a network location.

        Args:
            url: The URL to validate.

        Returns:
            True for supported URLs, False otherwise.
        """
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def read_feed_urls(self, csv_file: str) -> List[str]:
        """
        Read feed URLs from a CSV file.

        Args:
            csv_file: Path to the CSV file.

        Returns:
            A list of feed URLs.
        """
        urls = []
        seen_urls = set()
        try:
            with open(csv_file, "r", encoding="utf-8", newline="") as f:
                feed_list = csv.reader(f)
                for line_number, feed in enumerate(feed_list, start=1):
                    if not feed or not any(cell.strip() for cell in feed):
                        continue

                    url = feed[0].strip()
                    if not url:
                        logger.warning(f"Skipping invalid feed URL on line {line_number} in {csv_file}")
                        continue

                    if url.startswith("#"):
                        continue

                    if not self.is_supported_url(url):
                        logger.warning(f"Skipping unsupported feed URL on line {line_number} in {csv_file}")
                        continue

                    if url in seen_urls:
                        logger.info(f"Skipping duplicate feed URL on line {line_number} in {csv_file}")
                        continue

                    seen_urls.add(url)
                    urls.append(url)
            logger.info(f"Read {len(urls)} feed URLs from {csv_file}")
        except IOError as e:
            logger.error(f"Failed to read feed URLs from {csv_file}: {e}")

        return urls

    def fetch_feed_entries(self, url: str) -> List[Dict[str, Any]]:
        """
        Fetch entries from a feed URL.

        Args:
            url: The feed URL.

        Returns:
            A list of feed entries.
        """
        try:
            feed = feedparser.parse(url)
            if getattr(feed, "bozo", False):
                logger.warning(f"Feed parser reported malformed content for {url}: {feed.bozo_exception}")
            logger.info(f"Fetched {len(feed.entries)} entries from {url}")
            return feed.entries
        except Exception as e:
            logger.error(f"Failed to fetch feed from {url}: {e}")
            return []

    @staticmethod
    def html_to_text(html: str) -> str:
        """
        Convert HTML content into plain text.

        Args:
            html: HTML or text content.

        Returns:
            Extracted plain text.
        """
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        if paragraphs:
            return " ".join(paragraph for paragraph in paragraphs if paragraph)

        return soup.get_text(" ", strip=True)

    def extract_entry_content(self, entry: Dict[str, Any]) -> str:
        """
        Extract the most useful body content from the feed entry itself.

        Args:
            entry: The feed entry.

        Returns:
            Extracted body text if available.
        """
        for item in entry.get("content", []):
            content = self.html_to_text(item.get("value", ""))
            if content:
                return content

        for key in ("summary", "description"):
            content = self.html_to_text(entry.get(key, ""))
            if content:
                return content

        return ""

    def extract_content(self, url: str) -> str:
        """
        Extract text content from a URL.

        Args:
            url: The URL to extract content from.

        Returns:
            The extracted text content.
        """
        try:
            response = requests.get(url, headers=self.ARTICLE_REQUEST_HEADERS, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
            content = " ".join(paragraph for paragraph in paragraphs if paragraph)
            if not content:
                content = soup.get_text(" ", strip=True)

            logger.debug(f"Extracted {len(content)} characters from {url}")
            return content
        except RequestException as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error extracting content from {url}: {e}")
            return ""

    def process_entry(self, entry: Dict[str, Any], current_date: str) -> bool:
        """
        Process a single feed entry.

        Args:
            entry: The feed entry to process.
            current_date: The current date in ISO format.

        Returns:
            True if the entry was processed successfully, False otherwise.
        """
        try:
            title = clean_text(entry.get("title", "Untitled"))
            title = title.strip() or "Untitled"
            link = entry.get("link", "").strip()

            if not link:
                logger.warning(f"Entry '{title}' has no link, skipping")
                return False

            if self.dry_run:
                logger.info(f"[DRY RUN] Would process '{title}' ({link})")
                return True

            body = self.extract_entry_content(entry)
            if not body:
                body = self.extract_content(link)

            if not body:
                logger.warning(f"Failed to extract content for '{title}', using empty body")
                body = "No content extracted"

            safe_body = clean_text(body)
            date_struct = entry.get("published_parsed")
            date_str = format_date(date_struct, current_date)

            if self.notion_client is None:
                logger.error("Notion client is not configured")
                return False

            result = self.notion_client.add_page(title, link, safe_body, date_str)
            return result is not None

        except Exception as e:
            logger.error(f"Failed to process entry: {e}")
            return False

    def process_feed(self, url: str) -> int:
        """
        Process a single feed.

        Args:
            url: The feed URL to process.

        Returns:
            The number of successfully processed entries.
        """
        entries = self.fetch_feed_entries(url)
        if not entries:
            return 0

        deduplicated_entries = []
        seen_links = set()
        for entry in entries:
            link = entry.get("link", "").strip()
            if link and link in seen_links:
                logger.info(f"Skipping duplicate entry link '{link}' from {url}")
                continue

            if link:
                seen_links.add(link)
            deduplicated_entries.append(entry)

        if self.max_entries_per_feed is not None and len(deduplicated_entries) > self.max_entries_per_feed:
            logger.info(f"Limiting entries from {url} to first {self.max_entries_per_feed}")
            deduplicated_entries = deduplicated_entries[:self.max_entries_per_feed]

        current_date = get_current_date_iso()
        success_count = 0
        worker_count = min(self.max_workers, len(deduplicated_entries))

        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(self.process_entry, entry, current_date): entry
                for entry in deduplicated_entries
            }

            for future in concurrent.futures.as_completed(futures):
                entry = futures[future]
                try:
                    if future.result():
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")

        logger.info(f"Successfully processed {success_count}/{len(deduplicated_entries)} entries from {url}")
        return success_count

    def process_feed_urls(self, urls: List[str], max_feeds: Optional[int] = None) -> int:
        """
        Process a list of feed URLs.

        Args:
            urls: Feed URLs to process.
            max_feeds: Optional limit on the number of feeds to process.

        Returns:
            The number of successfully processed feeds.
        """
        if not urls:
            logger.warning("No feed URLs were provided")
            return 0

        selected_urls = urls
        if max_feeds is not None and len(urls) > max_feeds:
            logger.info(f"Limiting feeds to first {max_feeds} URLs")
            selected_urls = urls[:max_feeds]

        success_count = 0
        for url in selected_urls:
            try:
                processed = self.process_feed(url)
                if processed > 0:
                    success_count += 1
            except Exception as e:
                logger.error(f"Error processing feed {url}: {e}")

        logger.info(f"Successfully processed {success_count}/{len(selected_urls)} feeds")
        return success_count

    def process_feeds(self, csv_file: str, max_feeds: Optional[int] = None) -> int:
        """
        Process all feeds from a CSV file.

        Args:
            csv_file: Path to the CSV file containing feed URLs.
            max_feeds: Optional limit on the number of feeds to process.

        Returns:
            The number of successfully processed feeds.
        """
        urls = self.read_feed_urls(csv_file)
        if not urls:
            logger.warning(f"No feed URLs found in {csv_file}")
            return 0

        return self.process_feed_urls(urls, max_feeds=max_feeds)

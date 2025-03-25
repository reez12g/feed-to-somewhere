"""Feed processing module for Feed to Somewhere."""

import csv
import concurrent.futures
from typing import List, Optional, Dict, Any
import feedparser
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

from .logger import logger
from .utils import clean_text, format_date, get_current_date_iso
from .notion_client import NotionClient


class FeedProcessor:
    """Processor for RSS feeds."""

    def __init__(self, notion_client: Optional[NotionClient] = None, max_workers: int = 10):
        """
        Initialize the feed processor.

        Args:
            notion_client: The Notion client to use. If None, a new client is created.
            max_workers: Maximum number of worker threads to use.
        """
        self.notion_client = notion_client or NotionClient()
        self.max_workers = max_workers

    def read_feed_urls(self, csv_file: str) -> List[str]:
        """
        Read feed URLs from a CSV file.

        Args:
            csv_file: Path to the CSV file.

        Returns:
            A list of feed URLs.
        """
        urls = []
        try:
            with open(csv_file, "r") as f:
                feed_list = csv.reader(f)
                urls = [feed[0] for feed in feed_list]
            logger.info(f"Read {len(urls)} feed URLs from {csv_file}")
        except (IOError, IndexError) as e:
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
            logger.info(f"Fetched {len(feed.entries)} entries from {url}")
            return feed.entries
        except Exception as e:
            logger.error(f"Failed to fetch feed from {url}: {e}")
            return []

    def extract_content(self, url: str) -> str:
        """
        Extract text content from a URL.

        Args:
            url: The URL to extract content from.

        Returns:
            The extracted text content.
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            content = " ".join(p.text for p in paragraphs)
            
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
            link = entry.get("link", "")
            
            if not link:
                logger.warning(f"Entry '{title}' has no link, skipping")
                return False
            
            body = self.extract_content(link)
            if not body:
                logger.warning(f"Failed to extract content for '{title}', using empty body")
                body = "No content extracted"
            
            safe_body = clean_text(body)
            date_struct = entry.get("published_parsed")
            date_str = format_date(date_struct, current_date)
            
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
        
        current_date = get_current_date_iso()
        success_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_entry, entry, current_date): entry for entry in entries}
            
            for future in concurrent.futures.as_completed(futures):
                entry = futures[future]
                try:
                    if future.result():
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error processing entry {entry.get('title', 'Unknown')}: {e}")
        
        logger.info(f"Successfully processed {success_count}/{len(entries)} entries from {url}")
        return success_count

    def process_feeds(self, csv_file: str) -> int:
        """
        Process all feeds from a CSV file.

        Args:
            csv_file: Path to the CSV file containing feed URLs.

        Returns:
            The number of successfully processed feeds.
        """
        urls = self.read_feed_urls(csv_file)
        if not urls:
            logger.warning(f"No feed URLs found in {csv_file}")
            return 0
        
        success_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_feed, url): url for url in urls}
            
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                try:
                    processed = future.result()
                    if processed > 0:
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error processing feed {url}: {e}")
        
        logger.info(f"Successfully processed {success_count}/{len(urls)} feeds")
        return success_count

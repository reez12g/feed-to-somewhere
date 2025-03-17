import csv
import re
import feedparser
import requests
from bs4 import BeautifulSoup
from notion_client import Client
from notion_client.errors import APIResponseError
from datetime import datetime
import os
from threading import Thread


notion_token = os.getenv("NOTION_API_KEY")
database_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=notion_token)


def check_page_exists(title):
    """Check if a page with the specified title exists in the database."""
    query = notion.databases.query(
        database_id=database_id, filter={"property": "Name", "title": {"equals": title}}
    )
    return len(query["results"]) > 0


def add_text_chunks_to_page(page_id, text, chunk_size=2000):
    """Add text to a page by dividing it into chunks."""
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
    for chunk in chunks:
        notion.blocks.children.append(
            block_id=page_id,
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    },
                }
            ],
        )


def add_to_notion(title, link, body, date):
    """Add a new page to Notion. Skip if it already exists."""
    try:
        if check_page_exists(title):
            print(f"Page '{title}' already exists.")
            return
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "URL": {"url": link},
                "Date": {"date": {"start": date}},
            },
        )
        add_text_chunks_to_page(new_page["id"], body)
    except APIResponseError as e:
        print(f"Failed to add page '{title}'. Error: {e}")


def clean_text(text):
    """Remove invalid Unicode characters from text."""
    return re.sub(r"[^\u0000-\uD7FF\uE000-\uFFFF]", "", text)


def fetch_and_process_feeds(csv_file):
    """Read feeds from a CSV file and process them."""
    current_date_iso = datetime.now().date().isoformat()

    threads = []
    with open(csv_file, "r") as f:
        feed_list = csv.reader(f)
        for feed in feed_list:
            t = Thread(target=process_feed, args=(feed[0], current_date_iso))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()


def process_feed(url, current_date_iso):
    """Process an individual feed."""
    feed = feedparser.parse(url)
    threads = []
    for e in feed.entries:
        response = requests.get(e.link)
        safe_title = clean_text(e.title)
        body = " ".join(
            p.text for p in BeautifulSoup(response.content, "html.parser").find_all("p")
        )
        safe_body = clean_text(body)
        date = e.get("published_parsed")
        date_str = (
            f"{date.tm_year}-{date.tm_mon:02d}-{date.tm_mday:02d}"
            if date
            else current_date_iso
        )
        t = Thread(target=add_to_notion, args=(safe_title, e.link, safe_body, date_str))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    csv_file = "feed_list.csv"
    fetch_and_process_feeds(csv_file)

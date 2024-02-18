import csv
import re
import feedparser
import requests
from bs4 import BeautifulSoup
from notion_client import Client
from notion_client.errors import APIResponseError
from datetime import datetime
import os


notion_token = os.getenv("NOTION_API_KEY")
database_id = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=notion_token)


def check_page_exists(title):
    """指定したタイトルのページがデータベース内に存在するかチェック。"""
    query = notion.databases.query(
        database_id=database_id, filter={"property": "Name", "title": {"equals": title}}
    )
    return len(query["results"]) > 0


def add_text_chunks_to_page(page_id, text, chunk_size=2000):
    """テキストをチャンクに分割してページに追加。"""
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
    """Notionに新しいページを追加。存在する場合はスキップ。"""
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
    """テキストから不正なUnicode文字を除去。"""
    return re.sub(r"[^\u0000-\uD7FF\uE000-\uFFFF]", "", text)


def fetch_and_process_feeds(csv_file):
    """CSVファイルからフィードを読み込み、処理。"""
    current_date_iso = datetime.now().date().isoformat()
    with open(csv_file, "r") as f:
        feed_list = csv.reader(f)
        for feed in feed_list:
            process_feed(feed[0], current_date_iso)


def process_feed(url, current_date_iso):
    """個々のフィードを処理。"""
    feed = feedparser.parse(url)
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
        add_to_notion(safe_title, e.link, safe_body, date_str)


if __name__ == "__main__":
    csv_file = "feed_list.csv"
    fetch_and_process_feeds(csv_file)

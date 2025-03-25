#!/usr/bin/env python3
"""
Feed to Somewhere - A Python script that reads RSS feeds and saves them to a Notion database.

This is the main entry point for the application.
"""

import sys
from src.feed_to_somewhere.main import main

if __name__ == "__main__":
    sys.exit(main())

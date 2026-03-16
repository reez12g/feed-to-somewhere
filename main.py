#!/usr/bin/env python3
"""
Feed to Somewhere - A Python script that reads RSS feeds and saves them to a Notion database.

This is the main entry point for the application.
"""

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from feed_to_somewhere.main import main

if __name__ == "__main__":
    sys.exit(main())

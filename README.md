# Feed to Somewhere

A Python script that reads RSS feeds and saves them to a Notion database.

## Features

- Reads feed URLs from a CSV file
- Fetches feed entries and extracts text
- Saves entries to a Notion database
- Parallel processing using multithreading

## Environment Variables

The following environment variables must be set:

- `NOTION_API_KEY`: Notion API authentication key
- `NOTION_DATABASE_ID`: ID of the Notion database to store data

## Usage

```bash
python main.py
```

Each line in the CSV file (feed_list.csv) should contain a feed URL.

## Testing

This project includes two types of tests:

1. `test_main.py` - Tests using unittest
2. `test_main_pytest.py` - Tests using pytest

To run the tests:

```bash
# Run all tests
pytest

# Run only unittest style tests
python -m unittest test_main.py

# Run only pytest style tests
pytest test_main_pytest.py
```

## Dependencies

- beautifulsoup4
- feedparser
- notion-client
- requests
- pytest (for testing)

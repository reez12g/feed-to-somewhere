# Feed to Somewhere

A Python application that reads RSS feeds and saves them to a Notion database.

## Features

- Reads feed URLs from a CSV file
- Fetches feed entries and extracts text content
- Saves entries to a Notion database
- Parallel processing using thread pools
- Robust error handling and logging
- Configurable via environment variables and command-line arguments

## Environment Variables

The following environment variables can be set:

- `NOTION_API_KEY`: Notion API authentication key (required)
- `NOTION_DATABASE_ID`: ID of the Notion database to store data (required)
- `FEED_LIST_PATH`: Path to the CSV file containing feed URLs (default: `feed_list.csv`)
- `CHUNK_SIZE`: Maximum size of text chunks when adding to Notion (default: `2000`)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/feed-to-somewhere.git
cd feed-to-somewhere

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage
python main.py

# With command-line arguments
python main.py --feed-file custom_feeds.csv --max-workers 20 --log-level DEBUG
```

### Command-line Arguments

- `--feed-file`: Path to CSV file containing feed URLs (default: value from `FEED_LIST_PATH` or `feed_list.csv`)
- `--max-workers`: Maximum number of worker threads (default: `10`)
- `--log-level`: Set the logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, default: `INFO`)

### CSV File Format

Each line in the CSV file should contain a feed URL:

```
http://example.com/feed.xml
http://another-site.com/rss
```

## Docker

You can also run the application using Docker:

```bash
# Build the Docker image
docker build -t feed-to-somewhere .

# Run the container
docker run -e NOTION_API_KEY=your_key -e NOTION_DATABASE_ID=your_db_id feed-to-somewhere
```

## Project Structure

```
feed-to-somewhere/
├── src/
│   └── feed_to_somewhere/
│       ├── __init__.py
│       ├── config.py        # Configuration handling
│       ├── feed_processor.py # Feed processing logic
│       ├── logger.py        # Logging setup
│       ├── main.py          # Package entry point
│       ├── notion_client.py # Notion API client
│       └── utils.py         # Utility functions
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
├── Dockerfile               # Docker configuration
└── README.md                # This file
```

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

- beautifulsoup4 - HTML parsing
- feedparser - RSS feed parsing
- notion-client - Notion API integration
- requests - HTTP requests
- pytest - Testing

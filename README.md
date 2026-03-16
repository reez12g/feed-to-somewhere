# Feed to Somewhere

A Python application that reads RSS feeds and saves them to a Notion database.

## Features

- Reads feed URLs from a CSV file
- Reuses feed-provided article content before fetching full pages
- Saves entries to a Notion database with URL-based deduplication
- Parallel processing with bounded worker counts
- Robust error handling and logging
- Configurable via environment variables and command-line arguments

## Environment Variables

The following environment variables can be set:

- `NOTION_API_KEY`: Notion API authentication key (required)
- `NOTION_DATA_SOURCE_ID`: ID of the target Notion data source (preferred)
- `NOTION_DATABASE_ID`: Legacy database ID used to resolve a child data source automatically
- `FEED_LIST_PATH`: Path to the CSV file containing feed URLs (default: `feed_list.csv`)
- `CHUNK_SIZE`: Maximum size of text chunks when adding to Notion (default: `2000`)

## Requirements

- Python `3.10` or later

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd feed-to-somewhere

# Install the application
pip install .
```

## Usage

```bash
# Basic usage
feed-to-somewhere

# With command-line arguments
feed-to-somewhere --feed-file custom_feeds.csv --max-workers 20 --log-level DEBUG

# Repository-local wrapper without installation
python3 main.py --feed-file custom_feeds.csv
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
docker run --rm \
  -e NOTION_API_KEY=your_key \
  -e NOTION_DATA_SOURCE_ID=your_data_source_id \
  feed-to-somewhere
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
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_feed_processor.py # Tests for feed processor
│   ├── test_main.py         # Tests for main module
│   ├── test_notion_client.py # Tests for Notion client
│   └── test_utils.py        # Tests for utilities
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
├── requirements-dev.txt     # Development dependencies
├── Dockerfile               # Docker configuration
├── setup.py                 # Package installation
├── pytest.ini               # Pytest configuration
└── README.md                # This file
```

## Testing

This project uses pytest for testing. The tests are organized in the `tests/` directory.

To run the tests:

```bash
# Install the package with development dependencies
pip install -e . -r requirements-dev.txt

# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v
```

Tests do not require live Notion credentials. External API calls are mocked.

## Development

### Installation for Development

```bash
# Clone the repository
git clone <your-repo-url>
cd feed-to-somewhere

# Install in development mode
pip install -e . -r requirements-dev.txt
```

### Package Installation

You can also install the package directly:

```bash
pip install .
```

This will make the `feed-to-somewhere` command available in your environment.

## Dependencies

- beautifulsoup4 - HTML parsing
- feedparser - RSS feed parsing
- notion-client - Notion API integration with data source support
- requests - HTTP requests
- python-dotenv - Optional `.env` loading
- pytest - Testing only, via `requirements-dev.txt`

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
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_feed_processor.py # Tests for feed processor
│   ├── test_main.py         # Tests for main module
│   ├── test_notion_client.py # Tests for Notion client
│   └── test_utils.py        # Tests for utilities
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
├── Dockerfile               # Docker configuration
├── setup.py                 # Package installation
├── pytest.ini               # Pytest configuration
└── README.md                # This file
```

## Testing

This project uses pytest for testing. The tests are organized in the `tests/` directory.

To run the tests:

```bash
# Install the package in development mode
pip install -e .

# Run all tests
pytest

# Run tests for a specific module
pytest tests/test_utils.py

# Run tests with verbose output
pytest -v
```

### Environment Variables for Testing

When running tests, you'll need to set the required environment variables:

```bash
# For Unix/Linux/macOS
export NOTION_API_KEY=your_key
export NOTION_DATABASE_ID=your_db_id

# For Windows Command Prompt
set NOTION_API_KEY=your_key
set NOTION_DATABASE_ID=your_db_id

# For Windows PowerShell
$env:NOTION_API_KEY="your_key"
$env:NOTION_DATABASE_ID="your_db_id"
```

Alternatively, you can create a `.env` file in the project root with these variables:

```
NOTION_API_KEY=your_key
NOTION_DATABASE_ID=your_db_id
```

And use a package like `python-dotenv` to load them.

## Development

### Installation for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/feed-to-somewhere.git
cd feed-to-somewhere

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest
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
- notion-client - Notion API integration
- requests - HTTP requests
- pytest - Testing (development only)

# YouTube Channel Tracker

A production-ready service that tracks the latest videos from specified YouTube channels without using the YouTube API. The service stores the latest video for each channel and maintains a history of replaced videos.

## Features

- Track multiple YouTube channels via channel IDs
- Store latest video details (title, URL, thumbnail, description)
- Fetch and store related web content for each video
- Automatically search and store first 5 URLs with context
- Keep history of replaced videos
- Configurable check intervals
- Comprehensive logging system
- Docker containerization
- PostgreSQL database
- Log monitoring with Dozzle

## Project Structure

```
.
├── config/
│   └── env.example         # Example environment configuration
├── docker/
│   └── Dockerfile         # Docker image definition
├── logs/                  # Log files directory
├── src/
│   └── youtube_tracker/   # Main package
│       ├── __init__.py
│       ├── __main__.py   # Entry point
│       └── tracker.py    # Core functionality
├── tests/                # Test files
├── .env                  # Environment configuration
├── .gitignore           # Git ignore rules
├── docker-compose.yml   # Docker services configuration
└── requirements.txt     # Python dependencies
```

## Database Schema

### latest_videos
- channel_id (PK): YouTube channel ID
- video_id: YouTube video ID
- title: Video title
- url: Video URL
- thumbnail: Thumbnail URL
- description: First 100 words of video description
- web_search_results: JSON array of related web content
  - url: Related webpage URL
  - title: Page title
  - snippet: Search result snippet
  - context: First 1000 characters of page content
- updated_at: Last update timestamp

### processed_videos
- id (PK): Auto-incrementing ID
- channel_id: YouTube channel ID
- video_id: YouTube video ID
- title: Video title
- url: Video URL
- thumbnail: Thumbnail URL
- description: Video description
- web_search_results: JSON array of related web content (same structure as above)
- processed_at: Processing timestamp
- action: Type of processing ('replaced')

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd youtube-tracker
```

2. Create environment file:
```bash
cp config/env.example .env
```

3. Edit .env file with your YouTube channel IDs and desired configuration.

4. Start the services:
```bash
docker-compose up -d
```

## Monitoring

### Logs
- Console logs are available via Docker logs:
```bash
docker-compose logs -f tracker
```

- File logs are stored in the `logs` directory
- Web-based log viewer (Dozzle) available at http://localhost:8080

### Database
- PostgreSQL is exposed on port 5432
- Connect using your preferred database tool:
  - Host: localhost
  - Port: 5432
  - Database: youtube_tracker
  - User: postgres
  - Password: postgres

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the tracker:
```bash
python -m youtube_tracker
```

## Testing

The project includes comprehensive tests for all components, including the web search functionality.

### Running Tests

Run all tests with coverage report:
```bash
pytest --cov=src/youtube_tracker tests/
```

Run specific test file:
```bash
pytest tests/test_web_search.py -v
```

### Test Structure

- `tests/conftest.py`: PyTest configuration and fixtures
- `tests/test_web_search.py`: Tests for web search functionality
  - Search result validation
  - Error handling
  - Page content extraction
  - Response structure verification

### Test Coverage

Tests cover:
- Successful web searches
- Empty search results
- Request error handling
- Page content extraction
- Result structure validation
- HTML parsing and cleaning

### Manual Testing Script

A script is provided to test the web search functionality with custom parameters:

```bash
# Basic usage
python scripts/test_web_search.py --query "your search query"

# Specify number of results
python scripts/test_web_search.py --query "python programming" --results 3

# Custom log file
python scripts/test_web_search.py --query "test query" --log-file custom_log.log

# Save results to JSON
python scripts/test_web_search.py --query "test query" --output results.json
```

The script provides:
- Detailed logging of search results
- Formatted output for easy reading
- Option to save results as JSON
- Automatic log file creation with timestamps
- Error handling and reporting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

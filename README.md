# YouTube Channel Tracker

A production-ready service that tracks the latest videos from specified YouTube channels without using the YouTube API. The service stores the latest video for each channel and maintains a history of replaced videos.

## Features

- Track multiple YouTube channels via channel IDs
- Store latest video details (title, URL, thumbnail, description)
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
- updated_at: Last update timestamp

### processed_videos
- id (PK): Auto-incrementing ID
- channel_id: YouTube channel ID
- video_id: YouTube video ID
- title: Video title
- url: Video URL
- thumbnail: Thumbnail URL
- description: Video description
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

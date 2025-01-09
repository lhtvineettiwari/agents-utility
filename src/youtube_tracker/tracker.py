import os
import time
import schedule
import logging
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import requests
from bs4 import BeautifulSoup
import re
from .web_search import WebSearcher

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure file handler
file_handler = logging.FileHandler('logs/youtube_tracker.log')
file_handler.setFormatter(log_format)

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, log_level))
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'youtube_tracker')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# Create database connection
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define database models
Base = declarative_base()

class LatestVideo(Base):
    __tablename__ = "latest_videos"

    channel_id = Column(String, primary_key=True)
    video_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    description = Column(String)
    web_search_results = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ProcessedVideo(Base):
    __tablename__ = "processed_videos"

    id = Column(Integer, primary_key=True)
    channel_id = Column(String, nullable=False)
    video_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    description = Column(String)
    web_search_results = Column(JSON, nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)
    action = Column(String, nullable=False)  # 'replaced' or 'removed'

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize web searcher
web_searcher = WebSearcher()

def perform_web_search(title, description):
    """
    Perform web search based on video title and description.
    """
    try:
        # Combine title and first few words of description for search
        desc_words = description.split()[:20] if description else []
        search_query = f"{title} {' '.join(desc_words)}"
        
        logger.info(f"Performing web search for: {search_query[:100]}...")
        results = web_searcher.search(search_query)
        
        if results:
            logger.info(f"Found {len(results)} web search results")
        else:
            logger.warning("No web search results found")
            
        return results
    except Exception as e:
        logger.error(f"Error performing web search: {str(e)}")
        return []

def get_latest_video(channel_id):
    """
    Fetch the latest video details from a YouTube channel without using the API.
    """
    try:
        logger.debug(f"Fetching latest video for channel {channel_id}")
        
        # Construct the channel's videos page URL
        channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"
        
        # Send request with headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()
        
        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the script tag containing video information
        scripts = soup.find_all('script')
        video_data = None
        
        for script in scripts:
            if script.string and '"videoRenderer"' in script.string:
                match = re.search(r'"videoRenderer":({.+?})}', script.string)
                if match:
                    video_data = match.group(1)
                    break
        
        if not video_data:
            logger.warning(f"No video data found for channel {channel_id}")
            return None
            
        # Extract basic video information using regex
        video_id_match = re.search(r'"videoId":"(.*?)"', video_data)
        title_match = re.search(r'"title":{"runs":\[{"text":"(.*?)"}', video_data)
        thumbnail_match = re.search(r'"thumbnail":{"thumbnails":\[{"url":"(.*?)"', video_data)
        
        if not all([video_id_match, title_match, thumbnail_match]):
            logger.warning(f"Could not extract all required fields for channel {channel_id}")
            return None
            
        video_id = video_id_match.group(1)
        title = title_match.group(1)
        thumbnail_url = thumbnail_match.group(1)
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Fetch video page to get description
        video_response = requests.get(video_url, headers=headers)
        video_response.raise_for_status()
        
        # Find the script tag containing video description
        description = ""
        video_soup = BeautifulSoup(video_response.text, 'html.parser')
        for script in video_soup.find_all('script'):
            if script.string and '"description":{"simpleText":"' in script.string:
                desc_match = re.search(r'"description":{"simpleText":"(.*?)"}', script.string)
                if desc_match:
                    full_description = desc_match.group(1)
                    # Decode any HTML entities and unicode escapes
                    full_description = full_description.encode().decode('unicode-escape').replace('\\n', ' ').strip()
                    words = full_description.split()
                    description = ' '.join(words[:100])
                    if len(words) > 100:
                        description += "..."
                    break
        
        # Perform web search for context
        web_search_results = perform_web_search(title, description)
        
        logger.debug(f"Successfully fetched video data for channel {channel_id}")
        return {
            "channel_id": channel_id,
            "video_id": video_id,
            "title": title,
            "url": video_url,
            "thumbnail": thumbnail_url,
            "description": description,
            "web_search_results": web_search_results
        }
        
    except Exception as e:
        logger.error(f"Error fetching video for channel {channel_id}: {str(e)}")
        return None

def update_latest_videos():
    """
    Check for new videos and update the database.
    """
    logger.info("Starting video update check")
    try:
        # Get channel IDs from environment
        channel_ids = os.getenv('YOUTUBE_CHANNEL_IDS', '').split(',')
        if not channel_ids or not channel_ids[0]:
            logger.error("No channel IDs configured in .env file")
            return

        # Create database session
        db = SessionLocal()
        updates_found = False
        
        try:
            for channel_id in channel_ids:
                channel_id = channel_id.strip()
                if not channel_id:
                    continue
                    
                logger.info(f"Checking channel: {channel_id}")
                    
                # Get latest video for channel
                video_data = get_latest_video(channel_id)
                if not video_data:
                    logger.warning(f"Could not fetch video data for channel {channel_id}")
                    continue
                
                # Check if we already have this video
                existing_video = db.query(LatestVideo).filter_by(channel_id=channel_id).first()
                
                if existing_video:
                    if existing_video.video_id != video_data['video_id']:
                        # Store the existing video in processed_videos
                        processed_video = ProcessedVideo(
                            channel_id=existing_video.channel_id,
                            video_id=existing_video.video_id,
                            title=existing_video.title,
                            url=existing_video.url,
                            thumbnail=existing_video.thumbnail,
                            description=existing_video.description,
                            web_search_results=existing_video.web_search_results,
                            action='replaced'
                        )
                        db.add(processed_video)
                        
                        # Update the existing record
                        for key, value in video_data.items():
                            setattr(existing_video, key, value)
                        existing_video.updated_at = datetime.utcnow()
                        
                        logger.info(f"New video found for channel {channel_id}: {video_data['title']}")
                        updates_found = True
                    else:
                        logger.info(f"No new video for channel {channel_id}")
                else:
                    # Create new record
                    new_video = LatestVideo(**video_data, updated_at=datetime.utcnow())
                    db.add(new_video)
                    logger.info(f"Added first video for channel {channel_id}: {video_data['title']}")
                    updates_found = True
                
                db.commit()
                
        finally:
            db.close()
            
        if not updates_found:
            logger.info("No new videos found in this check")
            
    except Exception as e:
        logger.error(f"Error in update_latest_videos: {str(e)}")

def main():
    """
    Main function to run the tracker with scheduling.
    """
    # Get check interval from environment (default to 15 minutes)
    check_interval = int(os.getenv('CHECK_INTERVAL', '15'))
    
    logger.info(f"YouTube Tracker starting... (Checking every {check_interval} minutes)")
    
    # Run initial check
    update_latest_videos()
    
    # Schedule regular checks
    schedule.every(check_interval).minutes.do(update_latest_videos)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()

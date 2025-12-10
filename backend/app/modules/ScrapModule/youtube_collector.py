import os
import requests
from datetime import datetime
from ...config.mongo import MongoDB
from dotenv import load_dotenv
from flask import jsonify,current_app
import logging

# Create a regular logger for background jobs
logger = logging.getLogger(__name__)


from pathlib import Path
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


class YouTubeCollector:

    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.ins = MongoDB()
        self.db = self.ins.db

    # --------------------------------------------------------------
    # Fetch Trending Videos (Sri Lanka)
    # --------------------------------------------------------------
    def fetch_trending(self, region="LK", max_results=20):
        url = f"{self.base_url}/videos"
        params = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region,
            "maxResults": max_results,
            "key": self.api_key
        }

        try:
            resp = requests.get(url, params=params)
            data = resp.json()

            videos = []
            for item in data.get("items", []):
                videos.append({
                    "type": "trending",
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "published_at": item["snippet"]["publishedAt"],
                    "views": item["statistics"].get("viewCount"),
                    "likes": item["statistics"].get("likeCount"),
                    "comments": item["statistics"].get("commentCount"),
                    "scraped_at": datetime.utcnow().isoformat()
                })
            self.ins.insert_many("youtube_trending", videos)
            # return videos
            logger.error(f"YouTube Trending Videos: {videos}")

        except Exception as e:
            logger.error("YouTube Trending Error:", e)
            # return []

    # --------------------------------------------------------------
    # Search Videos By Keyword
    # --------------------------------------------------------------
    def search_videos(self, query, max_results=10):
        url = f"{self.base_url}/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": self.api_key
        }

        try:
            resp = requests.get(url, params=params)
            data = resp.json()

            results = []
            for item in data.get("items", []):
                results.append({
                    "type": "search",
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "published_at": item["snippet"]["publishedAt"],
                    "query": query,
                    "scraped_at": datetime.utcnow().isoformat()
                })
            # self.db.insert_many("youtube_search", results)
            # return results
            logger.error(f"YouTube Search Results: {results}")

        except Exception as e:
            logger.error(f"YouTube Search Error:", e)
            # return []

    
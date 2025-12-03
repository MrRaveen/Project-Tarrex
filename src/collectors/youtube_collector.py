import os
import requests
from datetime import datetime
from src.database.mongo import MongoDB
from dotenv import load_dotenv



from pathlib import Path
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


class YouTubeCollector:

    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.db = MongoDB()

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
            self.db.insert_many("youtube_trending", videos)
            return videos

        except Exception as e:
            print("YouTube Trending Error:", e)
            return []

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
            self.db.insert_many("youtube_search", results)
            return results

        except Exception as e:
            print("YouTube Search Error:", e)
            return []

    # --------------------------------------------------------------
    # Fetch Channel Statistics
    # --------------------------------------------------------------
    def fetch_channel_stats(self, channel_id):
        url = f"{self.base_url}/channels"
        params = {
            "part": "snippet,statistics",
            "id": channel_id,
            "key": self.api_key
        }

        try:
            resp = requests.get(url, params=params)
            data = resp.json()

            if not data.get("items"):
                return {}

            item = data["items"][0]

            stats = {
                "type": "channel_stats",
                "channel_id": channel_id,
                "title": item["snippet"]["title"],
                "subscribers": item["statistics"].get("subscriberCount"),
                "views": item["statistics"].get("viewCount"),
                "videos": item["statistics"].get("videoCount"),
                "scraped_at": datetime.utcnow().isoformat()
            }
            self.db.insert_many("youtube_channels", [stats])

        except Exception as e:
            print("YouTube Channel Stats Error:", e)
            return {}

    # --------------------------------------------------------------
    # Fetch Video Statistics
    # --------------------------------------------------------------
    def fetch_video_stats(self, video_id):
        url = f"{self.base_url}/videos"
        params = {
            "part": "statistics,snippet",
            "id": video_id,
            "key": self.api_key
        }

        try:
            resp = requests.get(url, params=params)
            data = resp.json()

            if not data.get("items"):
                return {}

            item = data["items"][0]
            
            stats = {
                "type": "video_stats",
                "video_id": video_id,
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "views": item["statistics"].get("viewCount"),
                "likes": item["statistics"].get("likeCount"),
                "comments": item["statistics"].get("commentCount"),
                "scraped_at": datetime.utcnow().isoformat()
            }
            self.db.insert_many("youtube_videos", [stats])

        except Exception as e:
            print("YouTube Video Stats Error:", e)
            return {}

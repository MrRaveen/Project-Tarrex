import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.database.mongo import MongoDB
import os

# Load .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)


class RedditCollector:

    def __init__(self):
        self.base_url = "https://api.pullpush.io/reddit/search"
        self.db = MongoDB()

    # ---------------------------------------------------------------------
    # FETCH HOT POSTS FROM A SUBREDDIT (REAL-TIME)
    # ---------------------------------------------------------------------
    def fetch_hot(self, subreddit="srilanka", limit=10):
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"

        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            data = resp.json()

            posts = []
            for item in data["data"]["children"]:
                post = item["data"]
                posts.append({
                    "type": "reddit_hot",
                    "subreddit": subreddit,
                    "title": post.get("title"),
                    "url": "https://reddit.com" + post.get("permalink", ""),
                    "score": post.get("score"),
                    "num_comments": post.get("num_comments"),
                    "created_utc": post.get("created_utc"),
                    "scraped_at": datetime.utcnow().isoformat()
                })
            self.db.insert_many("reddit", posts)
            return posts

        except Exception as e:
            print("Reddit Hot Error:", e)
            return []

    # ---------------------------------------------------------------------
    # FETCH NEW POSTS FROM A SUBREDDIT
    # ---------------------------------------------------------------------
    def fetch_new(self, subreddit="srilanka", limit=10):
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"

        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            data = resp.json()

            posts = []
            for item in data["data"]["children"]:
                post = item["data"]
                posts.append({
                    "type": "reddit_new",
                    "subreddit": subreddit,
                    "title": post.get("title"),
                    "url": "https://reddit.com" + post.get("permalink", ""),
                    "score": post.get("score"),
                    "num_comments": post.get("num_comments"),
                    "created_utc": post.get("created_utc"),
                    "scraped_at": datetime.utcnow().isoformat()
                })
            self.db.insert_many("reddit", posts)
            return posts

        except Exception as e:
            print("Reddit New Error:", e)
            return []

    # ---------------------------------------------------------------------
    # FETCH TOP POSTS FROM A SUBREDDIT
    # ---------------------------------------------------------------------
    def fetch_top(self, subreddit="srilanka", limit=10, time_filter="day"):
        url = f"https://www.reddit.com/r/{subreddit}/top.json?t={time_filter}&limit={limit}"

        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            data = resp.json()

            posts = []
            for item in data["data"]["children"]:
                post = item["data"]
                posts.append({
                    "type": "reddit_top",
                    "subreddit": subreddit,
                    "title": post.get("title"),
                    "url": "https://reddit.com" + post.get("permalink", ""),
                    "score": post.get("score"),
                    "num_comments": post.get("num_comments"),
                    "created_utc": post.get("created_utc"),
                    "scraped_at": datetime.utcnow().isoformat()
                })
            
            self.db.insert_many("reddit", posts)
            return posts

        except Exception as e:
            print("Reddit Top Error:", e)
            return []

    # ---------------------------------------------------------------------
    # KEYWORD SEARCH (PUSHSHIFT API)
    # ---------------------------------------------------------------------
    def search(self, query, limit=20):
        url = f"https://api.pullpush.io/reddit/search/submission/"
        params = {
            "q": query,
            "size": limit,
            "sort": "desc",
            "sort_type": "score"
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()

            posts = []
            for post in data.get("data", []):
                posts.append({
                    "type": "reddit_search",
                    "query": query,
                    "title": post.get("title"),
                    "url": post.get("full_link"),
                    "score": post.get("score"),
                    "num_comments": post.get("num_comments"),
                    "created_utc": post.get("created_utc"),
                    "scraped_at": datetime.utcnow().isoformat()
                })
                
            self.db.insert_many("reddit", posts)
            return posts

        except Exception as e:
            print("Reddit Search Error:", e)
            return []

import requests
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

api_key = os.getenv("YOUTUBE_API_KEY")

url = "https://www.googleapis.com/youtube/v3/search"
params = {
    "part": "snippet",
    "q": "NewsFirst Sri Lanka",
    "type": "channel",
    "key": api_key,
    "maxResults": 3
}

resp = requests.get(url, params=params)
print(resp.json())

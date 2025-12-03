import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.youtube_collector import YouTubeCollector

yt = YouTubeCollector()

print("\nFetching trending videos...")
trending = yt.fetch_trending()
print(trending[:3])

print("\nSearching videos for 'Sri Lanka news'...")
search = yt.search_videos("Sri Lanka news")
print(search[:3])

print("\nFetching channel stats (NewsFirst)...")
channel = yt.fetch_channel_stats("UCNewfcqo9rMNNv8NzvHfQqQ")  # Example NewsFirst channel ID
print(channel)

print("\nFetching video stats (one video)...")
video = yt.fetch_video_stats("dQw4w9WgXcQ")  # Example video
print(video)

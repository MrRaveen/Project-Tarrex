import sys
import os

ys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))s

from src.collectors.google_trends_collector import GoogleTrendsCollector

collector = GoogleTrendsCollector()


print("\nFetching Top & Rising Queries...")
keywords = ["Sri Lanka", "weather", "cricket"]
tr = collector.fetch_top_and_rising(keywords)
print(tr[:5])

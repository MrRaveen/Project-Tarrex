"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.google_trends_collector import GoogleTrendsCollector

collector = GoogleTrendsCollector()


print("\nFetching Top & Rising Queries...")
keywords = ["Sri Lanka", "weather", "cricket"]
tr = collector.fetch_top_and_rising(keywords)
print(tr[:5])
"""
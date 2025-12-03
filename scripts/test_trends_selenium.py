"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.google_trends_selenium import GoogleTrendsSelenium

collector = GoogleTrendsSelenium()

data = collector.fetch_trending_now("LK")
print(data)

"""
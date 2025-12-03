import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.reddit_collector import RedditCollector

r = RedditCollector()

print("\nFetching HOT posts...")
print(r.fetch_hot("srilanka")[:3])

print("\nFetching NEW posts...")
print(r.fetch_new("srilanka")[:3])

print("\nFetching TOP posts...")
print(r.fetch_top("srilanka")[:3])

print("\nSearching for keyword 'Sri Lanka economy'...")
print(r.search("Sri Lanka economy")[:3])

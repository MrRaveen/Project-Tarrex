import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.news_collector import NewsCollector

collector = NewsCollector()

print("Fetching AdaDerana...")
ada = collector.fetch_adaderana()
print(ada[:3])

print("\nFetching NewsFirst...")
nf = collector.fetch_newsfirst()
print(nf[:3])

print("\nFetching DailyMirror...")
dm = collector.fetch_dailymirror()
print(dm[:3])

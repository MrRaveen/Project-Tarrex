import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.google_trends_new import GoogleTrendsNew

c = GoogleTrendsNew()
print(c.fetch_trending_now("LK", debug=True))

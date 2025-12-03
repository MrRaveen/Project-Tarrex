README — Tarrex Data Collection System (Phase 0–1 Completed)

This project collects real-time data about Sri Lanka from multiple sources (News, Google Trends, Weather, YouTube, Reddit) and stores everything in a single MongoDB database.

This is Phase 0–1 of a larger project.

✔ Completed So Far

1. Project Structure Created

Project-Tarrex/
│
├── src/
│   ├── collectors/
│   │   ├── news_collector.py
│   │   ├── trends_collector.py
│   │   ├── weather_collector.py
│   │   ├── youtube_collector.py
│   │   ├── reddit_collector.py
│   │
│   ├── database/
│   │   ├── mongo.py
│   │
│   ├── utils/
│       ├── helpers.py   (optional)
│
├── scripts/
│   ├── test_news.py
│   ├── test_trends.py
│   ├── test_weather.py
│   ├── test_youtube.py
│   ├── test_reddit.py
│
├── .env
├── requirements.txt
└── README.md

________________________________________

2. Virtual Environment Setup

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

All needed packages installed:
•	requests
•	pymongo
•	python-dotenv
•	beautifulsoup4
•	feedparser
•	google API client
•	pytrends
•	lxml
________________________________________

3. Environment File (.env) Configured

.env contains:
GOOGLE_API_KEY="YOUR_API_KEY"
WEATHER_API_KEY="YOUR_API_KEY"

MONGO_URI="mongodb+srv://..."
DB_NAME="tarrex"
________________________________________
4. MongoDB Connected Successfully

We use:

•	MongoDB Atlas
•	pymongo client
•	Automatic unique index for URLs in news collector
•	Duplicate insert protection

Collections created so far:

news
reddit
youtube_trending
youtube_search
youtube_channels
youtube_videos
weather_now
weather_forecast
________________________________________

5. Collectors Completed & Saving to MongoDB

✔ News Collector (AdaDerana, NewsFirst, DailyMirror)
•	Scrapes HTML and RSS
•	Stores articles in news collection
•	Duplicate URLs ignored automatically

✔ Reddit Collector
•	Uses pullpush.io API
•	Fetches hot, new, top posts
•	Stores in reddit collection

✔ YouTube Collector
•	Trending videos
•	Video search
•	Channel stats
•	Video stats

Stored in:
youtube_trending
youtube_search
youtube_channels
youtube_videos

✔ Weather Collector
•	Current weather
•	5-day forecast
•	Stores in:

weather_now
weather_forecast

✔ Google Trends
PyTrends partially working (rate limited), 

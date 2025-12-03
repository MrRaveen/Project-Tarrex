import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

class NewsCollector:

    def fetch_adaderana(self):
        url = "https://www.adaderana.lk/hot-news"
        response = requests.get(url, timeout=10)

        articles = []

        if response.status_code != 200:
            print("Failed to load AdaDerana")
            return articles

        soup = BeautifulSoup(response.text, "lxml")
        news_blocks = soup.select(".news-story")  # CSS class used by AdaDerana

        for item in news_blocks:
            title = item.select_one("h2")
            time = item.select_one(".date")

            article = {
                "source": "AdaDerana",
                "title": title.text.strip() if title else None,
                "url": title.find("a")["href"] if title and title.find("a") else None,
                "published": time.text.strip() if time else None,
                "scraped_at": datetime.utcnow().isoformat()
            }

            articles.append(article)

        return articles
    
    def fetch_newsfirst(self):
        base = "https://english.newsfirst.lk"
        url = f"{base}/latest"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            print(f"Failed to load NewsFirst ({resp.status_code})")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        seen = set()
        articles = []

        # Find anchors that look like article links: href containing '/20' (e.g. /2025/12/03/...)
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            # skip anchors that are just page fragments or navigation
            if href.startswith("#") or href.lower().startswith("mailto:") or href.lower().startswith("javascript:"):
                continue

            # Accept absolute or relative links that contain '/20' (simple year pattern)
            if "/20" not in href:
                continue

            # Build absolute URL if needed
            if href.startswith("/"):
                full_url = base + href
            elif href.startswith("http"):
                full_url = href
            else:
                # uncommon relative form like '2025/12/03/...'
                full_url = base + "/" + href

            # basic dedupe
            if full_url in seen:
                continue
            seen.add(full_url)

            # Title: prefer the anchor text; if empty, try the link's title attribute
            title = a.get_text(strip=True) or a.get("title") or None
            if not title:
                # sometimes the link contains an image; try its alt
                img = a.find("img")
                if img and img.get("alt"):
                    title = img.get("alt").strip()

            articles.append({
                "source": "NewsFirst",
                "title": title,
                "url": full_url,
                "published": None,  # the listing page doesn't always include a machine-readable published field
                "scraped_at": datetime.utcnow().isoformat()
            })

            # stop when we have a reasonable number
            if len(articles) >= 30:
                break

        return articles



    
    def fetch_dailymirror(self):
        url = "https://www.dailymirror.lk/rss/latest-news/108"

        feed = feedparser.parse(url)
        articles = []

        for entry in feed.entries[:20]:
            articles.append({
                "source": "DailyMirror",
                "title": entry.title,
                "url": entry.link,
                "published": entry.get("published", None),
                "scraped_at": datetime.utcnow().isoformat()
            })

        return articles




    
    

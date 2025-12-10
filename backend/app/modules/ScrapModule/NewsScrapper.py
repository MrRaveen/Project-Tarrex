import datetime
from bs4 import BeautifulSoup
from flask import current_app, jsonify
import requests

from ...config import celery_app
from ...config.mongo import MongoDB
import logging

# Create a regular logger for background jobs
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.ins = MongoDB()
        self.db = self.ins.db
        self.headers = {'User-Agent': 'ModelX-SriLanka-Monitor/1.0 (+your-email@university.edu)'}

    def scrape_breaking_news(self):
        try:
            url = 'https://www.adaderana.lk/'
            
            # Add headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # Check if request was successful
            if response.status_code != 200:
                return jsonify({
                    "error": f"Failed to fetch page. Status code: {response.status_code}"
                }), response.status_code
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all story-text divs
            story_divs = soup.find_all("div", class_="story-text")
            
            news_items = []
            
            for story in story_divs:
                # Extract the <a> tag inside <h3>
                link_tag = story.find("h3").find("a") if story.find("h3") else None
                
                if link_tag:
                    # Extract href (might be relative URL)
                    href = link_tag.get('href', '')
                    # Make absolute URL if it's relative
                    if href and not href.startswith('http'):
                        href = url.rstrip('/') + '/' + href.lstrip('/')
                    
                    # Extract link text
                    title = link_tag.get_text(strip=True)
                    
                    # Extract the paragraph text
                    paragraph = story.find("p")
                    description = paragraph.get_text(strip=True) if paragraph else ""
                    
                    # Extract date from comments div
                    comments_div = story.find("div", class_="comments")
                    date_text = ""
                    if comments_div:
                        # Find the span containing date
                        span_tag = comments_div.find("span")
                        if span_tag:
                            # Remove "Comments (0)" text and extract date
                            date_text = span_tag.get_text(strip=True).replace('|', '').strip()
                    
                    news_items.append({
                        "title": title,
                        "link": href,
                        "description": description,
                        "date": date_text
                    })
            
            # Return JSON response
            # return jsonify({
            #     "success": True,
            #     "total_news": len(news_items),
            #     "news": news_items
            # })
            logger.error(f"{news_items}")
        except Exception as e:
            # return jsonify({
            #     "error": f"An error occurred: {str(e)}"
            # }), 500  
            logger.error(f"An error occurred: {str(e)}")  


import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from bs4 import BeautifulSoup
import time
import random

from ...model.news_model import NewsArticle, NewsBatch

logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.sources = [
            'newsfirst.lk',
            'adaderana.lk', 
            'dailynews.lk',
            'colombopage.com',
            'news.lk'
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_news_api(self, query: str = "Sri Lanka", language: str = "en") -> List[NewsArticle]:
        """Scrape news using News API"""
        if not self.api_key:
            logger.warning("News API key not configured")
            return []
            
        try:
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': language,
                'sortBy': 'publishedAt',
                'apiKey': self.api_key,
                'pageSize': 50,
                'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get('articles', []):
                try:
                    article = NewsArticle(
                        title=item.get('title', ''),
                        content=item.get('description', '') or item.get('content', ''),
                        source=item.get('source', {}).get('name', 'unknown'),
                        url=item.get('url', ''),
                        published_at=datetime.fromisoformat(item['publishedAt'].replace('Z', '+00:00')),
                        category=self._categorize_article(item.get('title', ''), item.get('description', '')),
                        location=self._extract_location(item),
                        metadata={
                            'author': item.get('author'),
                            'urlToImage': item.get('urlToImage')
                        }
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error processing news article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"News API error: {e}")
            return []
    
    def scrape_web_direct(self) -> List[NewsArticle]:
        """Scrape news directly from Sri Lankan news websites"""
        articles = []
        
        # Scrape NewsFirst
        try:
            articles.extend(self._scrape_newsfirst())
        except Exception as e:
            logger.error(f"Error scraping NewsFirst: {e}")
        
        # Scrape Ada Derana
        try:
            articles.extend(self._scrape_adaderana())
        except Exception as e:
            logger.error(f"Error scraping Ada Derana: {e}")
        
        # Scrape Daily News
        try:
            articles.extend(self._scrape_dailynews())
        except Exception as e:
            logger.error(f"Error scraping Daily News: {e}")
        
        return articles
    
    def _scrape_newsfirst(self) -> List[NewsArticle]:
        """Scrape NewsFirst.lk"""
        url = "https://www.newsfirst.lk/category/local/"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        for article_div in soup.select('.post-item'):
            try:
                title_elem = article_div.select_one('.post-title a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                url = title_elem['href']
                
                # Get full article content
                content = self._get_article_content(url)
                
                date_elem = article_div.select_one('.post-date')
                published_at = datetime.now()
                if date_elem:
                    try:
                        date_str = date_elem.get_text(strip=True)
                        published_at = self._parse_date(date_str)
                    except:
                        pass
                
                article = NewsArticle(
                    title=title,
                    content=content,
                    source="NewsFirst",
                    url=url,
                    published_at=published_at,
                    category="local",
                    location="Sri Lanka",
                    metadata={
                        'scraped_via': 'web_direct'
                    }
                )
                articles.append(article)
                
            except Exception as e:
                logger.error(f"Error processing NewsFirst article: {e}")
                continue
        
        return articles
    
    def _scrape_adaderana(self) -> List[NewsArticle]:
        """Scrape AdaDerana.lk"""
        url = "https://www.adaderana.lk/hot-news"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        for news_item in soup.select('.news-story'):
            try:
                title_elem = news_item.select_one('h2 a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                url = "https://www.adaderana.lk" + title_elem['href']
                
                content_elem = news_item.select_one('.story-text')
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                date_elem = news_item.select_one('.comments')
                published_at = datetime.now()
                
                article = NewsArticle(
                    title=title,
                    content=content,
                    source="Ada Derana",
                    url=url,
                    published_at=published_at,
                    category="hot-news",
                    location="Sri Lanka",
                    metadata={
                        'scraped_via': 'web_direct'
                    }
                )
                articles.append(article)
                
            except Exception as e:
                logger.error(f"Error processing Ada Derana article: {e}")
                continue
        
        return articles
    
    def _scrape_dailynews(self) -> List[NewsArticle]:
        """Scrape DailyNews.lk"""
        url = "http://www.dailynews.lk"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        for headline in soup.select('.headline'):
            try:
                title_elem = headline.select_one('a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                url = title_elem['href']
                if not url.startswith('http'):
                    url = "http://www.dailynews.lk" + url
                
                # Get full content
                content = self._get_article_content(url)
                
                article = NewsArticle(
                    title=title,
                    content=content,
                    source="Daily News",
                    url=url,
                    published_at=datetime.now(),
                    category="headlines",
                    location="Sri Lanka",
                    metadata={
                        'scraped_via': 'web_direct'
                    }
                )
                articles.append(article)
                
            except Exception as e:
                logger.error(f"Error processing Daily News article: {e}")
                continue
        
        return articles
    
    def _get_article_content(self, url: str) -> str:
        """Get full article content from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Different selectors for different news sites
            content_selectors = [
                '.article-content',
                '.story-content',
                '.post-content',
                '.entry-content',
                'article',
                '.content',
                '.main-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    paragraphs = content_elem.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    return content[:2000]  # Limit content length
            
            return ""
            
        except Exception as e:
            logger.error(f"Error getting article content from {url}: {e}")
            return ""
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        try:
            # Simple date parsing - can be enhanced
            return datetime.now()
        except:
            return datetime.now()
    
    def _categorize_article(self, title: str, content: str) -> str:
        """Categorize article based on content"""
        text = (title + " " + content).lower()
        
        categories = {
            'political': ['president', 'minister', 'government', 'parliament', 'election', 'policy'],
            'economic': ['economy', 'gdp', 'inflation', 'budget', 'tax', 'market', 'business'],
            'social': ['education', 'health', 'school', 'hospital', 'community', 'social'],
            'sports': ['cricket', 'football', 'sports', 'match', 'tournament'],
            'technology': ['tech', 'digital', 'computer', 'internet', 'software'],
            'environment': ['environment', 'climate', 'weather', 'pollution', 'conservation']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "general"
    
    def _extract_location(self, article_data: Dict[str, Any]) -> str:
        """Extract location from article data"""
        # Simple location extraction - can be enhanced with NLP
        text = (article_data.get('title', '') + " " + article_data.get('description', '')).lower()
        
        sri_lankan_locations = [
            'colombo', 'kandy', 'galle', 'jaffna', 'trincomalee', 'anuradhapura',
            'matara', 'ratnapura', 'badulla', 'kurunegala', 'negombo', 'gampaha'
        ]
        
        for location in sri_lankan_locations:
            if location in text:
                return location.capitalize()
        
        return "Sri Lanka"
    
    def collect_news(self) -> NewsBatch:
        """Main method to collect news from all sources"""
        logger.info("Starting news collection...")
        
        all_articles = []
        
        # Use News API if available
        if self.api_key:
            api_articles = self.scrape_news_api("Sri Lanka")
            all_articles.extend(api_articles)
            logger.info(f"Collected {len(api_articles)} articles from News API")
        
        # Scrape direct from websites
        web_articles = self.scrape_web_direct()
        all_articles.extend(web_articles)
        logger.info(f"Collected {len(web_articles)} articles from web scraping")
        
        # Remove duplicates based on title similarity
        unique_articles = self._remove_duplicates(all_articles)
        
        batch = NewsBatch(
            articles=unique_articles,
            source="multiple",
            scrape_timestamp=datetime.now()
        )
        
        logger.info(f"Total unique articles collected: {len(unique_articles)}")
        return batch
    
    def _remove_duplicates(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Simple duplicate detection - can be enhanced with fuzzy matching
            title_key = article.title.lower().strip()
            if title_key not in seen_titles and len(title_key) > 10:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
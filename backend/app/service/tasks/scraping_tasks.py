from celery import shared_task
from app.modules.ScrapModule.news_collector import NewsCollector
from app.modules.ScrapModule.trends_collector import TrendsCollector
from app.modules.ScrapModule.youtube_collector import YouTubeCollector
from app.modules.ScrapModule.weather_collector import WeatherCollector
from app.modules.ScrapModule.pricing_collector import PricingCollector
from app.modules.ScrapModule.tax_collector import TaxCollector
from app.modules.ingestionLayer.data_ingestor import DataIngestor
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, name="scrape_news_task")
def scrape_news_task(self):
    """Celery task to scrape news data"""
    try:
        logger.info("Starting news scraping task")
        collector = NewsCollector()
        news_data = collector.scrape_news()
        
        # Ingest the scraped data
        ingestor = DataIngestor()
        result = ingestor.ingest_news_data(news_data)
        
        logger.info(f"News scraping task completed: {len(news_data)} articles processed")
        return {
            "status": "success",
            "articles_processed": len(news_data),
            "ingested_count": result.get("ingested_count", 0)
        }
    except Exception as e:
        logger.error(f"News scraping task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="scrape_trends_task")
def scrape_trends_task(self):
    """Celery task to scrape Google Trends data"""
    try:
        logger.info("Starting trends scraping task")
        collector = TrendsCollector()
        trends_data = collector.get_trends_data()
        
        # Ingest the scraped data
        ingestor = DataIngestor()
        result = ingestor.ingest_trends_data(trends_data)
        
        logger.info(f"Trends scraping task completed: {len(trends_data)} trends processed")
        return {
            "status": "success",
            "trends_processed": len(trends_data),
            "ingested_count": result.get("ingested_count", 0)
        }
    except Exception as e:
        logger.error(f"Trends scraping task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="scrape_youtube_task")
def scrape_youtube_task(self):
    """Celery task to scrape YouTube data"""
    try:
        logger.info("Starting YouTube scraping task")
        collector = YouTubeCollector()
        youtube_data = collector.get_youtube_data()
        
        # Ingest the scraped data
        ingestor = DataIngestor()
        result = ingestor.ingest_youtube_data(youtube_data)
        
        logger.info(f"YouTube scraping task completed: {len(youtube_data)} videos processed")
        return {
            "status": "success",
            "videos_processed": len(youtube_data),
            "ingested_count": result.get("ingested_count", 0)
        }
    except Exception as e:
        logger.error(f"YouTube scraping task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="scrape_weather_task")
def scrape_weather_task(self):
    """Celery task to scrape weather data"""
    try:
        logger.info("Starting weather scraping task")
        collector = WeatherCollector()
        weather_data = collector.get_current_weather()
        
        # Ingest the scraped data
        ingestor = DataIngestor()
        result = ingestor.ingest_weather_data(weather_data)
        
        logger.info(f"Weather scraping task completed: {len(weather_data)} locations processed")
        return {
            "status": "success",
            "locations_processed": len(weather_data),
            "ingested_count": result.get("ingested_count", 0)
        }
    except Exception as e:
        logger.error(f"Weather scraping task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="scrape_pricing_task")
def scrape_pricing_task(self):
    """Celery task to scrape food pricing data"""
    try:
        logger.info("Starting pricing scraping task")
        collector = PricingCollector()
        pricing_data = collector.get_food_prices()
        
        # Ingest the scraped data
        ingestor = DataIngestor()
        result = ingestor.ingest_pricing_data(pricing_data)
        
        logger.info(f"Pricing scraping task completed: {len(pricing_data)} items processed")
        return {
            "status": "success",
            "items_processed": len(pricing_data),
            "ingested_count": result.get("ingested_count", 0)
        }
    except Exception as e:
        logger.error(f"Pricing scraping task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="scrape_tax_task")
def scrape_tax_task(self):
    """Celery task to scrape tax revenue data"""
    try:
        logger.info("Starting tax scraping task")
        collector = TaxCollector()
        tax_data = collector.get_tax_revenue_data()
        
        # Ingest the scraped data
        ingestor = DataIngestor()
        result = ingestor.ingest_tax_data(tax_data)
        
        logger.info(f"Tax scraping task completed: {len(tax_data)} records processed")
        return {
            "status": "success",
            "records_processed": len(tax_data),
            "ingested_count": result.get("ingested_count", 0)
        }
    except Exception as e:
        logger.error(f"Tax scraping task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="scrape_all_data_task")
def scrape_all_data_task(self):
    """Celery task to scrape all data types"""
    try:
        logger.info("Starting comprehensive data scraping task")
        
        # Execute all scraping tasks sequentially
        news_result = scrape_news_task.apply()
        trends_result = scrape_trends_task.apply()
        youtube_result = scrape_youtube_task.apply()
        weather_result = scrape_weather_task.apply()
        pricing_result = scrape_pricing_task.apply()
        tax_result = scrape_tax_task.apply()
        
        logger.info("Comprehensive data scraping task completed")
        return {
            "status": "success",
            "news": news_result.result,
            "trends": trends_result.result,
            "youtube": youtube_result.result,
            "weather": weather_result.result,
            "pricing": pricing_result.result,
            "tax": tax_result.result
        }
    except Exception as e:
        logger.error(f"Comprehensive scraping task failed: {str(e)}")
        raise self.retry(exc=e, countdown=600, max_retries=2)

import atexit

from flask import current_app

from ..ScrapModule.foodPricingScrap import scrapFoodPricingAll
from ..ScrapModule.taxRevenueGather import scrapTaxRevenueDataAll
from ..ScrapModule.weatherCollector import WeatherCollector
from ..ScrapModule.youtube_collector import YouTubeCollector
from ..ScrapModule.NewsScrapper import NewsScraper
from ...config.ap_scheduler import AP_scheduler
from apscheduler.triggers.interval import IntervalTrigger

import logging

# Create a regular logger for background jobs
logger = logging.getLogger(__name__)
# Create scheduler instance but DON'T start it here
scheduler = AP_scheduler()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
newsObj = NewsScraper()
ytCollector = YouTubeCollector()
weatherCollector = WeatherCollector()
scrapTaxRevenueDataObj = scrapTaxRevenueDataAll()
getFoodPricingObj = scrapFoodPricingAll()
def addJobs():
    """Add all scheduled jobs to the scheduler"""
    try:
        if not scheduler:
            current_app.logger.error("Scheduler instance is not available.")
            return
        
        # Clear any existing jobs
        scheduler.remove_all_jobs()
        # For news 
        # scheduler.add_job(
        #     id='scrape_news',
        #     func=lambda: newsObj.scrape_breaking_news(),
        #     trigger=IntervalTrigger(seconds=10),
        #     replace_existing=True
        # )
        
        # For youtube
        # scheduler.add_job(
        #     id='youtube_collect',
        #     func=lambda: ytCollector.fetch_trending(),
        #     trigger=IntervalTrigger(seconds=20),
        #     replace_existing=True
        # )
        
        # For weather
        # scheduler.add_job(
        #     id='scrape_weather',  # Changed from 'scrape_news'
        #     func=lambda: weatherCollector.fetch_current_weather_simple(),
        #     trigger=IntervalTrigger(seconds=30),
        #     replace_existing=True
        # )
        #tax revenue gather
        scheduler.add_job(
            id='tax_revenue_gather', 
            func=lambda: scrapTaxRevenueDataObj.scrapTaxRevenueData(),
            trigger=IntervalTrigger(seconds=120),
            replace_existing=True
        )
        #foodPricing scrap
        # scheduler.add_job(
        #     id='food_pricing_gather', 
        #     func=lambda: getFoodPricingObj.getFoodPricing(),
        #     trigger=IntervalTrigger(days=30),
        #     replace_existing=True
        # )
        logger.error(f"Jobs added to scheduler successfully. Total jobs: {len(scheduler.get_jobs())}")
        
    except Exception as e:    
        logger.error(f"Error adding jobs to scheduler: {e}")


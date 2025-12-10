from datetime import datetime
from venv import logger

from bs4 import BeautifulSoup
from flask import Blueprint, Flask, current_app, jsonify, request
import requests

# from ..modules.ScrapModule.taxRevenueGather import scrapTaxRevenueData

from ..modules.ingestionLayer.scheduler import scheduler as scheduler_instance

from ..modules.ScrapModule.weatherCollector import WeatherCollector

from ..modules.ScrapModule.youtube_collector import YouTubeCollector

from ..modules.ScrapModule.NewsScrapper import NewsScraper

user_bp = Blueprint('user', __name__)
@user_bp.route('/')
def index():
    return jsonify({
        "message": "Reddit Collector API",
        "endpoints": {
            "/test/hot": "Fetch hot posts from a subreddit",
            "/test/new": "Fetch new posts from a subreddit",
            "/test/top": "Fetch top posts from a subreddit",
            "/test/search": "Search posts by keyword"
        }
    })

@user_bp.route('/test/news/now', methods=['GET'])
def scrape_news_now():
    try:
        news_scraper = NewsScraper()
        return news_scraper.scrape_breaking_news()
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Network error: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
    
@user_bp.route('/test/yt/now', methods=['GET'])
def scrape_youtube_trending():
    try:
        yt_collector = YouTubeCollector()
        result = yt_collector.fetch_trending()
        
        # If fetch_trending returns a Flask response (jsonify), return it directly
        if hasattr(result, 'headers'):  # It's a Flask response
            return result
        
        # If it returns a list/dict, convert to JSON
        # Also handle any ObjectId if MongoDB returns them
        if isinstance(result, list):
            # Convert any MongoDB ObjectId to string
            for video in result:
                if '_id' in video and hasattr(video['_id'], '__str__'):
                    video['_id'] = str(video['_id'])
            
            return jsonify({
                "success": True,
                "count": len(result),
                "videos": result
            })
        
        # If it's a dict
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
@user_bp.route('/test/yt/search', methods=['GET'])
def search_yt_videos():
    try:
        yt_collector = YouTubeCollector()
        search = yt_collector.search_videos("Sri Lanka news")
        return jsonify({"data" : search})
    except Exception as e:
        return jsonify({"error" : str(e)}), 500            
@user_bp.route('/test/weather/now',methods=['GET'])
def scrapeWeather():
    try:
        # ins = WeatherCollector()
        # output = ins.fetch_current_weather()
        # return output
        # In your Flask route or test script
        weather = WeatherCollector()
        print("Testing WeatherCollector...")
        print(f"API Key exists: {bool(weather.api_key)}")
        result = weather.fetch_current_weather_simple()
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        return result
    except Exception as e:
        return jsonify({"error" : str(e)}), 500        

# @user_bp.route('/test/taxData',methods=['GET'])
# def get_tax_data():
#     try:
#         data = scrapTaxRevenueData()
#         logger.error(f"{data}")
#         return jsonify({"msg": "sucess"})
#     except Exception as e:
#         return jsonify({"error" : str(e)}), 500  


# @user_bp.route('/test/getFoodPrice',methods=['GET'])
# def get_food_price():
#     try:
#         from ..modules.ScrapModule.foodPricingScrap import getFoodPricing
#         data = getFoodPricing()
#         return jsonify({"data" : data})
#     except Exception as e:
#         return jsonify({"error" : str(e)}), 500

@user_bp.route('/test/weather/forecast',methods=['GET'])
def get_forecast():
    try:
        weather = WeatherCollector()
        result = weather.fetch_forecast()
        return result
    except Exception as e:
        return jsonify({"error" : str(e)}), 500
    
@user_bp.route('/scheduler/status', methods=['GET'])
def scheduler_status():
    """Check scheduler status"""
    status = {
        'running': scheduler_instance.running,
        'job_count': len(scheduler_instance.get_jobs()),
        'jobs': [],
        'current_time': str(datetime.now())
    }
    
    for job in scheduler_instance.get_jobs():
        status['jobs'].append({
            'id': job.id,
            'name': job.name,
            'next_run': str(job.next_run_time) if job.next_run_time else 'None',
            'trigger': str(job.trigger)
        })
    
    return jsonify(status)

@user_bp.route('/test/log', methods=['POST'])   
def log_msg():
    current_app.logger.error("This is a test error log message.")
    return jsonify({"message": "Log message sent."})
    
    
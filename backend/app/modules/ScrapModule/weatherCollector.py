import os
from flask import jsonify,current_app
import requests
from datetime import datetime
from dotenv import load_dotenv
from ...config.mongo import MongoDB
import logging

# Create a regular logger for background jobs
logger = logging.getLogger(__name__)
load_dotenv()

class WeatherCollector:

    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.default_city = "Colombo"
        self.country = "LK"
        self.ins = MongoDB()
        self.db = self.ins.db

    def fetch_current_weather_simple(self, city="Colombo"):
        city = city or self.default_city
        url = f"{self.base_url}/weather"
        params = {
            "q": f"{city},{self.country}",
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            # Just return the raw data without MongoDB
            # return jsonify({
            #     "success": True,
            #     "api_response": data,
            #     "processed": {
            #         "city": city,
            #         "temp": data.get("main", {}).get("temp"),
            #         "description": data.get("weather", [{}])[0].get("description")
            #     }
            # })
            logger.error(f"Weather Data: {data}")
        except Exception as e:
            logger.error(f"Weather Error: {str(e)}")

    def fetch_forecast(self, city="Colombo"):
        """
        Returns a 5-day / 3-hour forecast.
        """
        city = city or self.default_city

        url = f"{self.base_url}/forecast"
        params = {
            "q": f"{city},{self.country}",
            "appid": self.api_key,
            "units": "metric"
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()

            forecast_list = []
            for item in data["list"]:
                forecast_list.append({
                    "city": city,
                    "time": item["dt_txt"],
                    "temp": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "description": item["weather"][0]["description"],
                    "scraped_at": datetime.utcnow().isoformat()
                })
                
              #TODO: in the ML part  
            # self.ins.db.insert_many("weather_forecast", forecast_list)
            # return jsonify({"data" : forecast_list})
            logger.error(f"Weather forecast Data: {forecast_list}")

        except Exception as e:
            logger.error(f"error: {e}")

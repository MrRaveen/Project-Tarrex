import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class WeatherCollector:

    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.default_city = "Colombo"
        self.country = "LK"

    def fetch_current_weather(self, city=None):
        """
        Returns current weather conditions for a Sri Lankan city.
        """
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

            return {
                "city": city,
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "scraped_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            print("Weather Error:", str(e))
            return {}

    def fetch_forecast(self, city=None):
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

            return forecast_list

        except Exception as e:
            print("Forecast Error:", str(e))
            return []

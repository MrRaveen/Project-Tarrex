import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.weather_collector import WeatherCollector

collector = WeatherCollector()

print("\nFetching current weather (Colombo)...")
current = collector.fetch_current_weather()
print(current)

print("\nFetching 5-day forecast (Colombo)...")
forecast = collector.fetch_forecast()
print(forecast[:5])

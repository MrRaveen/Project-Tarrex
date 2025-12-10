import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from ...model.weather_model import WeatherData, WeatherBatch, WeatherCondition, MainWeatherData, WindData, CloudsData

logger = logging.getLogger(__name__)

class WeatherCollector:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Major cities and locations in Sri Lanka
        self.locations = [
            {'name': 'Colombo', 'lat': 6.9271, 'lon': 79.8612},
            {'name': 'Kandy', 'lat': 7.2906, 'lon': 80.6337},
            {'name': 'Galle', 'lat': 6.0329, 'lon': 80.2168},
            {'name': 'Jaffna', 'lat': 9.6615, 'lon': 80.0255},
            {'name': 'Trincomalee', 'lat': 8.5692, 'lon': 81.2331},
            {'name': 'Anuradhapura', 'lat': 8.3114, 'lon': 80.4037},
            {'name': 'Matara', 'lat': 5.9483, 'lon': 80.5353},
            {'name': 'Ratnapura', 'lat': 6.6844, 'lon': 80.3996},
            {'name': 'Badulla', 'lat': 6.9895, 'lon': 81.0557},
            {'name': 'Kurunegala', 'lat': 7.4863, 'lon': 80.3623}
        ]
    
    def get_current_weather(self, lat: float, lon: float, location_name: str) -> Optional[WeatherData]:
        """Get current weather data for a specific location"""
        if not self.api_key:
            logger.warning("Weather API key not configured")
            return self._get_simulated_weather(lat, lon, location_name)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse weather conditions
            weather_conditions = []
            for condition in data.get('weather', []):
                weather_conditions.append(WeatherCondition(
                    main=condition.get('main', ''),
                    description=condition.get('description', ''),
                    icon=condition.get('icon', '')
                ))
            
            # Parse main weather data
            main_data = data.get('main', {})
            main_weather = MainWeatherData(
                temp=main_data.get('temp', 0),
                feels_like=main_data.get('feels_like', 0),
                temp_min=main_data.get('temp_min', 0),
                temp_max=main_data.get('temp_max', 0),
                pressure=main_data.get('pressure', 0),
                humidity=main_data.get('humidity', 0),
                sea_level=main_data.get('sea_level'),
                grnd_level=main_data.get('grnd_level')
            )
            
            # Parse wind data
            wind_data = data.get('wind', {})
            wind = WindData(
                speed=wind_data.get('speed', 0),
                deg=wind_data.get('deg', 0),
                gust=wind_data.get('gust')
            )
            
            # Parse clouds data
            clouds_data = data.get('clouds', {})
            clouds = CloudsData(all=clouds_data.get('all', 0))
            
            # Parse timestamp
            timestamp = datetime.fromtimestamp(data.get('dt', 0))
            
            weather_data = WeatherData(
                location=location_name,
                coordinates={'lat': lat, 'lon': lon},
                timestamp=timestamp,
                weather_conditions=weather_conditions,
                main=main_weather,
                visibility=data.get('visibility'),
                wind=wind,
                rain=data.get('rain'),
                snow=data.get('snow'),
                clouds=clouds,
                dt=data.get('dt', 0),
                sys=data.get('sys', {}),
                timezone=data.get('timezone', 0),
                city_id=data.get('id', 0),
                city_name=data.get('name', location_name),
                metadata={
                    'base': data.get('base', ''),
                    'cod': data.get('cod', 0)
                }
            )
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather data for {location_name}: {e}")
            return self._get_simulated_weather(lat, lon, location_name)
    
    def get_weather_forecast(self, lat: float, lon: float, location_name: str) -> List[WeatherData]:
        """Get weather forecast for a specific location"""
        if not self.api_key:
            logger.warning("Weather API key not configured")
            return []
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            forecast_list = []
            
            for forecast_item in data.get('list', [])[:12]:  # Next 12 periods (36 hours)
                try:
                    # Parse weather conditions
                    weather_conditions = []
                    for condition in forecast_item.get('weather', []):
                        weather_conditions.append(WeatherCondition(
                            main=condition.get('main', ''),
                            description=condition.get('description', ''),
                            icon=condition.get('icon', '')
                        ))
                    
                    # Parse main weather data
                    main_data = forecast_item.get('main', {})
                    main_weather = MainWeatherData(
                        temp=main_data.get('temp', 0),
                        feels_like=main_data.get('feels_like', 0),
                        temp_min=main_data.get('temp_min', 0),
                        temp_max=main_data.get('temp_max', 0),
                        pressure=main_data.get('pressure', 0),
                        humidity=main_data.get('humidity', 0)
                    )
                    
                    # Parse wind data
                    wind_data = forecast_item.get('wind', {})
                    wind = WindData(
                        speed=wind_data.get('speed', 0),
                        deg=wind_data.get('deg', 0),
                        gust=wind_data.get('gust')
                    )
                    
                    # Parse clouds data
                    clouds_data = forecast_item.get('clouds', {})
                    clouds = CloudsData(all=clouds_data.get('all', 0))
                    
                    # Parse timestamp
                    timestamp = datetime.fromtimestamp(forecast_item.get('dt', 0))
                    
                    weather_data = WeatherData(
                        location=location_name,
                        coordinates={'lat': lat, 'lon': lon},
                        timestamp=timestamp,
                        weather_conditions=weather_conditions,
                        main=main_weather,
                        wind=wind,
                        rain=forecast_item.get('rain'),
                        snow=forecast_item.get('snow'),
                        clouds=clouds,
                        dt=forecast_item.get('dt', 0),
                        metadata={
                            'forecast': True,
                            'period': forecast_item.get('dt_txt', '')
                        }
                    )
                    
                    forecast_list.append(weather_data)
                    
                except Exception as e:
                    logger.error(f"Error processing forecast item: {e}")
                    continue
            
            return forecast_list
            
        except Exception as e:
            logger.error(f"Error getting weather forecast for {location_name}: {e}")
            return []
    
    def get_historical_weather(self, lat: float, lon: float, location_name: str, 
                              days: int = 7) -> List[WeatherData]:
        """Get historical weather data (simulated for demo)"""
        historical_data = []
        now = datetime.now()
        
        for i in range(days):
            date = now - timedelta(days=i)
            
            # Simulate historical weather data
            weather_data = WeatherData(
                location=location_name,
                coordinates={'lat': lat, 'lon': lon},
                timestamp=date,
                weather_conditions=[WeatherCondition(
                    main="Clear",
                    description="clear sky",
                    icon="01d"
                )],
                main=MainWeatherData(
                    temp=28 + random.uniform(-3, 3),
                    feels_like=30 + random.uniform(-3, 3),
                    temp_min=25 + random.uniform(-2, 2),
                    temp_max=32 + random.uniform(-2, 2),
                    pressure=1013 + random.randint(-10, 10),
                    humidity=70 + random.randint(-20, 20)
                ),
                wind=WindData(
                    speed=5 + random.uniform(-3, 3),
                    deg=random.randint(0, 360)
                ),
                clouds=CloudsData(all=random.randint(0, 100)),
                dt=int(date.timestamp()),
                metadata={
                    'historical': True,
                    'simulated': True
                }
            )
            
            historical_data.append(weather_data)
        
        return historical_data
    
    def _get_simulated_weather(self, lat: float, lon: float, location_name: str) -> WeatherData:
        """Generate simulated weather data for demo purposes"""
        now = datetime.now()
        
        # Simulate weather based on location and time
        if location_name.lower() in ['colombo', 'galle', 'matara']:
            # Coastal areas
            temp = 30 + random.uniform(-2, 2)
            humidity = 80 + random.randint(-10, 10)
            main_weather = "Clouds" if random.random() > 0.7 else "Clear"
        elif location_name.lower() in ['kandy', 'badulla', 'nuwaraeliya']:
            # Hill country
            temp = 22 + random.uniform(-3, 3)
            humidity = 85 + random.randint(-15, 15)
            main_weather = "Rain" if random.random() > 0.5 else "Clouds"
        else:
            # Other areas
            temp = 28 + random.uniform(-4, 4)
            humidity = 75 + random.randint(-15, 15)
            main_weather = "Clear" if random.random() > 0.6 else "Clouds"
        
        weather_data = WeatherData(
            location=location_name,
            coordinates={'lat': lat, 'lon': lon},
            timestamp=now,
            weather_conditions=[WeatherCondition(
                main=main_weather,
                description=f"{main_weather.lower()} sky",
                icon="01d" if main_weather == "Clear" else "02d"
            )],
            main=MainWeatherData(
                temp=temp,
                feels_like=temp + 2,
                temp_min=temp - 3,
                temp_max=temp + 3,
                pressure=1013 + random.randint(-10, 10),
                humidity=humidity
            ),
            wind=WindData(
                speed=5 + random.uniform(-3, 3),
                deg=random.randint(0, 360)
            ),
            clouds=CloudsData(all=random.randint(0, 100)),
            dt=int(now.timestamp()),
            metadata={
                'simulated': True,
                'source': 'simulation'
            }
        )
        
        return weather_data
    
    def collect_weather_data(self) -> WeatherBatch:
        """Main method to collect weather data for all locations"""
        logger.info("Starting weather data collection...")
        
        all_weather_data = []
        
        for location in self.locations:
            try:
                weather_data = self.get_current_weather(
                    location['lat'], 
                    location['lon'], 
                    location['name']
                )
                
                if weather_data:
                    all_weather_data.append(weather_data)
                    logger.info(f"Collected weather data for {location['name']}")
                
                # Be respectful with API calls
                if self.api_key:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error processing location {location['name']}: {e}")
                continue
        
        batch = WeatherBatch(
            weather_data=all_weather_data,
            scrape_timestamp=datetime.now()
        )
        
        logger.info(f"Collected weather data for {len(all_weather_data)} locations")
        return batch
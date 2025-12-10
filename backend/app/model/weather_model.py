from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class WeatherCondition(BaseModel):
    main: str
    description: str
    icon: str

class MainWeatherData(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    sea_level: Optional[int] = None
    grnd_level: Optional[int] = None

class WindData(BaseModel):
    speed: float
    deg: int
    gust: Optional[float] = None

class RainData(BaseModel):
    one_hour: Optional[float] = Field(default=None, alias="1h")
    three_hours: Optional[float] = Field(default=None, alias="3h")

class SnowData(BaseModel):
    one_hour: Optional[float] = Field(default=None, alias="1h")
    three_hours: Optional[float] = Field(default=None, alias="3h")

class CloudsData(BaseModel):
    all: int

class WeatherData(BaseModel):
    location: str
    coordinates: Dict[str, float]
    timestamp: datetime
    weather_conditions: List[WeatherCondition]
    main: MainWeatherData
    visibility: Optional[int] = None
    wind: WindData
    rain: Optional[RainData] = None
    snow: Optional[SnowData] = None
    clouds: CloudsData
    dt: int
    sys: Dict[str, Any]
    timezone: int
    city_id: int
    city_name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WeatherBatch(BaseModel):
    weather_data: List[WeatherData]
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
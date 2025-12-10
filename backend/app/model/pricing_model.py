from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class PriceRecord(BaseModel):
    item: str
    price: float
    unit: str
    market: str
    location: str
    currency: str = Field(default="LKR")
    quality: Optional[str] = Field(default=None)
    source: str

class FoodPrice(BaseModel):
    date: datetime
    location: str
    market: str
    prices: List[PriceRecord]
    average_price: float
    price_change: Optional[float] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PriceBatch(BaseModel):
    price_data: List[FoodPrice]
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TrendDataPoint(BaseModel):
    timestamp: datetime
    value: int
    formatted_value: str
    formatted_axis: str

class TrendComparison(BaseModel):
    keyword: str
    geo: str
    time: str
    category: int

class TrendData(BaseModel):
    keyword: str
    geo: str = Field(default="LK")
    time_range: str = Field(default="now 7-d")
    category: int = Field(default=0)
    data_points: List[TrendDataPoint]
    averages: Dict[str, float]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TrendBatch(BaseModel):
    trends: List[TrendData]
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
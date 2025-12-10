from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class IndicatorType(str, Enum):
    ECONOMIC = "economic"
    SOCIAL = "social"
    POLITICAL = "political"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"
    SECURITY = "security"

class IndicatorTrend(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    VOLATILE = "volatile"

class Indicator(BaseModel):
    name: str
    type: IndicatorType
    value: float
    unit: str
    timestamp: datetime
    trend: IndicatorTrend
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class IndicatorBatch(BaseModel):
    indicators: List[Indicator]
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
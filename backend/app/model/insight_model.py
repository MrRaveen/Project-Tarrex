from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class InsightType(str, Enum):
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"

class InsightCategory(str, Enum):
    ECONOMIC = "economic"
    POLITICAL = "political"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"
    SECURITY = "security"
    BUSINESS = "business"

class Insight(BaseModel):
    title: str
    description: str
    type: InsightType
    category: InsightCategory
    confidence: float = Field(ge=0.0, le=1.0)
    impact: str = Field(default="medium")
    timeframe: str = Field(default="short_term")
    sources: List[str] = Field(default_factory=list)
    indicators: List[str] = Field(default_factory=list)
    recommendations: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InsightBatch(BaseModel):
    insights: List[Insight]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
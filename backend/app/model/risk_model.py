from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class RiskSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskCategory(str, Enum):
    ECONOMIC = "economic"
    POLITICAL = "political"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"

class Risk(BaseModel):
    title: str
    description: str
    category: RiskCategory
    severity: RiskSeverity
    probability: float = Field(ge=0.0, le=1.0)
    impact: float = Field(ge=0.0, le=1.0)
    timestamp: datetime
    location: str
    sources: List[str] = Field(default_factory=list)
    mitigation: Optional[str] = None
    trend: str = Field(default="stable")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RiskBatch(BaseModel):
    risks: List[Risk]
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
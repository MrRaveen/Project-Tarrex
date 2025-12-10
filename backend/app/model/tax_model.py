from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TaxCategory(BaseModel):
    category: str
    amount: float
    percentage: float
    target: Optional[float] = None
    variance: Optional[float] = None

class TaxRevenue(BaseModel):
    period: str  # e.g., "2024-Q1", "2024-01"
    period_type: str  # "monthly", "quarterly", "annual"
    total_revenue: float
    currency: str = Field(default="LKR")
    categories: List[TaxCategory]
    growth_rate: Optional[float] = None
    target_achievement: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TaxBatch(BaseModel):
    tax_data: List[TaxRevenue]
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
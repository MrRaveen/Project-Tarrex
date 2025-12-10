from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class NewsArticle(BaseModel):
    title: str
    content: str
    source: str
    url: str
    published_at: datetime
    category: str = Field(default="general")
    sentiment_score: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    keywords: List[str] = Field(default_factory=list)
    location: Optional[str] = Field(default=None)
    language: str = Field(default="en")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NewsBatch(BaseModel):
    articles: List[NewsArticle]
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
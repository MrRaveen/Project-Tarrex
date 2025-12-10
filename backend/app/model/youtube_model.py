from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class YouTubeThumbnail(BaseModel):
    url: str
    width: int
    height: int

class YouTubeVideo(BaseModel):
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    thumbnails: Dict[str, YouTubeThumbnail]
    view_count: int
    like_count: int
    comment_count: int
    duration: str
    category_id: str
    tags: List[str]
    default_audio_language: Optional[str] = None
    sentiment_score: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    keywords: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class YouTubeBatch(BaseModel):
    videos: List[YouTubeVideo]
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    search_query: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
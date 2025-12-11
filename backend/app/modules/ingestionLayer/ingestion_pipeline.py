import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import json

from ...config.mongo_config import mongo as get_mongo_client
from ...model.news_model import NewsBatch
from ...model.trends_model import TrendsBatch
from ...model.youtube_model import YouTubeBatch
from ...model.weather_model import WeatherBatch
from ...model.pricing_model import PriceBatch
from ...model.tax_model import TaxBatch

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self):
        self.mongo_client = get_mongo_client
        self.db = self.mongo_client.situational_awareness
        
        # Collections
        self.news_collection = self.db.news
        self.trends_collection = self.db.trends
        self.youtube_collection = self.db.youtube
        self.weather_collection = self.db.weather
        self.pricing_collection = self.db.pricing
        self.tax_collection = self.db.tax
        
        # Ensure indexes
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure MongoDB indexes for optimal query performance"""
        # News indexes
        self.news_collection.create_index([("published_at", -1)])
        self.news_collection.create_index([("source", 1)])
        self.news_collection.create_index([("category", 1)])
        self.news_collection.create_index([("title", "text"), ("content", "text")])
        
        # Trends indexes
        self.trends_collection.create_index([("timestamp", -1)])
        self.trends_collection.create_index([("keyword", 1)])
        self.trends_collection.create_index([("region", 1)])
        
        # YouTube indexes
        self.youtube_collection.create_index([("published_at", -1)])
        self.youtube_collection.create_index([("channel_id", 1)])
        self.youtube_collection.create_index([("title", "text"), ("description", "text")])
        
        # Weather indexes
        self.weather_collection.create_index([("timestamp", -1)])
        self.weather_collection.create_index([("location", 1)])
        self.weather_collection.create_index([("location_name", 1)])
        
        # Pricing indexes
        self.pricing_collection.create_index([("date", -1)])
        self.pricing_collection.create_index([("market", 1)])
        self.pricing_collection.create_index([("location", 1)])
        
        # Tax indexes
        self.tax_collection.create_index([("period", -1)])
        self.tax_collection.create_index([("source", 1)])
        self.tax_collection.create_index([("period_type", 1)])
        
        logger.info("MongoDB indexes ensured")
    
    def ingest_news(self, news_batch: NewsBatch) -> Dict[str, Any]:
        """Ingest news data into MongoDB"""
        try:
            news_data = [news.dict() for news in news_batch.news_data]
            
            # Add ingestion metadata
            for news in news_data:
                news['ingested_at'] = datetime.now()
                news['batch_id'] = news_batch.batch_id
                news['scrape_timestamp'] = news_batch.scrape_timestamp
            
            if news_data:
                result = self.news_collection.insert_many(news_data)
                logger.info(f"Ingested {len(result.inserted_ids)} news articles")
                return {
                    'success': True,
                    'inserted_count': len(result.inserted_ids),
                    'batch_id': news_batch.batch_id
                }
            
        except DuplicateKeyError:
            logger.warning("Duplicate news articles detected, skipping")
            return {'success': True, 'inserted_count': 0, 'duplicates': True}
            
        except Exception as e:
            logger.error(f"Error ingesting news: {e}")
            return {'success': False, 'error': str(e)}
    
    def ingest_trends(self, trends_batch: TrendsBatch) -> Dict[str, Any]:
        """Ingest trends data into MongoDB"""
        try:
            trends_data = [trend.dict() for trend in trends_batch.trends_data]
            
            # Add ingestion metadata
            for trend in trends_data:
                trend['ingested_at'] = datetime.now()
                trend['batch_id'] = trends_batch.batch_id
                trend['scrape_timestamp'] = trends_batch.scrape_timestamp
            
            if trends_data:
                result = self.trends_collection.insert_many(trends_data)
                logger.info(f"Ingested {len(result.inserted_ids)} trends records")
                return {
                    'success': True,
                    'inserted_count': len(result.inserted_ids),
                    'batch_id': trends_batch.batch_id
                }
            
        except DuplicateKeyError:
            logger.warning("Duplicate trends records detected, skipping")
            return {'success': True, 'inserted_count': 0, 'duplicates': True}
            
        except Exception as e:
            logger.error(f"Error ingesting trends: {e}")
            return {'success': False, 'error': str(e)}
    
    def ingest_youtube(self, youtube_batch: YouTubeBatch) -> Dict[str, Any]:
        """Ingest YouTube data into MongoDB"""
        try:
            youtube_data = [video.dict() for video in youtube_batch.videos]
            
            # Add ingestion metadata
            for video in youtube_data:
                video['ingested_at'] = datetime.now()
                video['batch_id'] = youtube_batch.batch_id
                video['scrape_timestamp'] = youtube_batch.scrape_timestamp
            
            if youtube_data:
                result = self.youtube_collection.insert_many(youtube_data)
                logger.info(f"Ingested {len(result.inserted_ids)} YouTube videos")
                return {
                    'success': True,
                    'inserted_count': len(result.inserted_ids),
                    'batch_id': youtube_batch.batch_id
                }
            
        except DuplicateKeyError:
            logger.warning("Duplicate YouTube videos detected, skipping")
            return {'success': True, 'inserted_count': 0, 'duplicates': True}
            
        except Exception as e:
            logger.error(f"Error ingesting YouTube data: {e}")
            return {'success': False, 'error': str(e)}
    
    def ingest_weather(self, weather_batch: WeatherBatch) -> Dict[str, Any]:
        """Ingest weather data into MongoDB"""
        try:
            weather_data = [weather.dict() for weather in weather_batch.weather_data]
            
            # Add ingestion metadata
            for weather in weather_data:
                weather['ingested_at'] = datetime.now()
                weather['batch_id'] = weather_batch.batch_id
                weather['scrape_timestamp'] = weather_batch.scrape_timestamp
            
            if weather_data:
                result = self.weather_collection.insert_many(weather_data)
                logger.info(f"Ingested {len(result.inserted_ids)} weather records")
                return {
                    'success': True,
                    'inserted_count': len(result.inserted_ids),
                    'batch_id': weather_batch.batch_id
                }
            
        except DuplicateKeyError:
            logger.warning("Duplicate weather records detected, skipping")
            return {'success': True, 'inserted_count': 0, 'duplicates': True}
            
        except Exception as e:
            logger.error(f"Error ingesting weather data: {e}")
            return {'success': False, 'error': str(e)}
    
    def ingest_pricing(self, pricing_batch: PriceBatch) -> Dict[str, Any]:
        """Ingest food pricing data into MongoDB"""
        try:
            pricing_data = [price.dict() for price in pricing_batch.price_data]
            
            # Add ingestion metadata
            for price in pricing_data:
                price['ingested_at'] = datetime.now()
                price['batch_id'] = pricing_batch.batch_id
                price['scrape_timestamp'] = pricing_batch.scrape_timestamp
            
            if pricing_data:
                result = self.pricing_collection.insert_many(pricing_data)
                logger.info(f"Ingested {len(result.inserted_ids)} pricing records")
                return {
                    'success': True,
                    'inserted_count': len(result.inserted_ids),
                    'batch_id': pricing_batch.batch_id
                }
            
        except DuplicateKeyError:
            logger.warning("Duplicate pricing records detected, skipping")
            return {'success': True, 'inserted_count': 0, 'duplicates': True}
            
        except Exception as e:
            logger.error(f"Error ingesting pricing data: {e}")
            return {'success': False, 'error': str(e)}
    
    def ingest_tax(self, tax_batch: TaxBatch) -> Dict[str, Any]:
        """Ingest tax revenue data into MongoDB"""
        try:
            tax_data = [tax.dict() for tax in tax_batch.tax_data]
            
            # Add ingestion metadata
            for tax in tax_data:
                tax['ingested_at'] = datetime.now()
                tax['batch_id'] = tax_batch.batch_id
                tax['scrape_timestamp'] = tax_batch.scrape_timestamp
            
            if tax_data:
                result = self.tax_collection.insert_many(tax_data)
                logger.info(f"Ingested {len(result.inserted_ids)} tax records")
                return {
                    'success': True,
                    'inserted_count': len(result.inserted_ids),
                    'batch_id': tax_batch.batch_id
                }
            
        except DuplicateKeyError:
            logger.warning("Duplicate tax records detected, skipping")
            return {'success': True, 'inserted_count': 0, 'duplicates': True}
            
        except Exception as e:
            logger.error(f"Error ingesting tax data: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics"""
        try:
            stats = {
                'news': self.news_collection.count_documents({}),
                'trends': self.trends_collection.count_documents({}),
                'youtube': self.youtube_collection.count_documents({}),
                'weather': self.weather_collection.count_documents({}),
                'pricing': self.pricing_collection.count_documents({}),
                'tax': self.tax_collection.count_documents({}),
                'last_updated': datetime.now().isoformat()
            }
            return stats
            
        except Exception as e:
            logger.error(f"Error getting ingestion stats: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")
from celery import shared_task
from app.modules.preprocessingLayer.preprocessing_pipeline import PreprocessingPipeline
from app.modules.preprocessingLayer.data_cleaner import DataCleaner
from app.modules.preprocessingLayer.text_preprocessor import TextPreprocessor
from app.modules.preprocessingLayer.normalization_engine import NormalizationEngine
from app.model.news_model import NewsArticle
from app.model.trends_model import TrendData
from app.model.youtube_model import YouTubeVideo
from app.model.weather_model import WeatherData
from app.model.pricing_model import FoodPrice
from app.model.tax_model import TaxRevenue
from app.config.mongo_config import get_database
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_mongo_collection(collection_name):
    """Get MongoDB collection"""
    db = get_database()
    return db[collection_name]

@shared_task(bind=True, name="process_data_task")
def process_data_task(self, data_type=None, batch_id=None):
    """Celery task to process raw data through preprocessing pipeline"""
    try:
        logger.info(f"Starting data processing task for {data_type or 'all data types'}")
        
        pipeline = PreprocessingPipeline()
        
        if data_type:
            # Process specific data type
            if data_type == "news":
                result = pipeline.process_news_data(batch_id)
            elif data_type == "trends":
                result = pipeline.process_trends_data(batch_id)
            elif data_type == "youtube":
                result = pipeline.process_youtube_data(batch_id)
            elif data_type == "weather":
                result = pipeline.process_weather_data(batch_id)
            elif data_type == "pricing":
                result = pipeline.process_pricing_data(batch_id)
            elif data_type == "tax":
                result = pipeline.process_tax_data(batch_id)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
        else:
            # Process all data types
            result = pipeline.process_all_data()
        
        logger.info(f"Data processing task completed: {result}")
        return {
            "status": "success",
            "result": result,
            "processed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Data processing task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="clean_data_task")
def clean_data_task(self, data_type, batch_id=None):
    """Celery task to clean specific data type"""
    try:
        logger.info(f"Starting data cleaning task for {data_type}")
        
        cleaner = DataCleaner()
        
        if data_type == "news":
            result = cleaner.clean_news_data(batch_id)
        elif data_type == "trends":
            result = cleaner.clean_trends_data(batch_id)
        elif data_type == "youtube":
            result = cleaner.clean_youtube_data(batch_id)
        elif data_type == "weather":
            result = cleaner.clean_weather_data(batch_id)
        elif data_type == "pricing":
            result = cleaner.clean_pricing_data(batch_id)
        elif data_type == "tax":
            result = cleaner.clean_tax_data(batch_id)
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        logger.info(f"Data cleaning task completed: {result}")
        return {
            "status": "success",
            "cleaned_count": result,
            "data_type": data_type
        }
    except Exception as e:
        logger.error(f"Data cleaning task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="preprocess_text_task")
def preprocess_text_task(self, data_type, batch_id=None):
    """Celery task to preprocess text data"""
    try:
        logger.info(f"Starting text preprocessing task for {data_type}")
        
        preprocessor = TextPreprocessor()
        
        if data_type == "news":
            result = preprocessor.preprocess_news_text(batch_id)
        elif data_type == "youtube":
            result = preprocessor.preprocess_youtube_text(batch_id)
        else:
            raise ValueError(f"Text preprocessing not supported for data type: {data_type}")
        
        logger.info(f"Text preprocessing task completed: {result} documents processed")
        return {
            "status": "success",
            "processed_count": result,
            "data_type": data_type
        }
    except Exception as e:
        logger.error(f"Text preprocessing task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="normalize_data_task")
def normalize_data_task(self, data_type, batch_id=None):
    """Celery task to normalize numerical data"""
    try:
        logger.info(f"Starting data normalization task for {data_type}")
        
        normalizer = NormalizationEngine()
        
        if data_type == "weather":
            result = normalizer.normalize_weather_data(batch_id)
        elif data_type == "pricing":
            result = normalizer.normalize_pricing_data(batch_id)
        elif data_type == "tax":
            result = normalizer.normalize_tax_data(batch_id)
        else:
            raise ValueError(f"Normalization not supported for data type: {data_type}")
        
        logger.info(f"Data normalization task completed: {result} records normalized")
        return {
            "status": "success",
            "normalized_count": result,
            "data_type": data_type
        }
    except Exception as e:
        logger.error(f"Data normalization task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="cleanup_old_data_task")
def cleanup_old_data_task(self, days_to_keep=30):
    """Celery task to cleanup old data from MongoDB"""
    try:
        logger.info(f"Starting cleanup of data older than {days_to_keep} days")
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        collections = ["news_articles", "trends_data", "youtube_videos", 
                      "weather_data", "food_prices", "tax_revenues",
                      "processed_news", "processed_trends", "processed_youtube",
                      "processed_weather", "processed_pricing", "processed_tax"]
        
        total_deleted = 0
        
        for collection_name in collections:
            try:
                collection = get_mongo_collection(collection_name)
                result = collection.delete_many({
                    "timestamp": {"$lt": cutoff_date}
                })
                deleted_count = result.deleted_count
                total_deleted += deleted_count
                logger.info(f"Cleaned up {deleted_count} documents from {collection_name}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {collection_name}: {str(e)}")
        
        logger.info(f"Cleanup task completed: {total_deleted} documents removed")
        return {
            "status": "success",
            "documents_deleted": total_deleted,
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise self.retry(exc=e, countdown=600, max_retries=2)
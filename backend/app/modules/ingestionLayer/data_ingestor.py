import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

from ...modules.ScrapModule.news_collector import NewsCollector
from ...modules.ScrapModule.trends_collector import TrendsCollector
from ...modules.ScrapModule.youtube_collector import YouTubeCollector
from ...modules.ScrapModule.weather_collector import WeatherCollector
from ...modules.ScrapModule.pricing_collector import PricingCollector
from ...modules.ScrapModule.tax_collector import TaxCollector

from .ingestion_pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

class DataIngestor:
    def __init__(self):
        self.ingestion_pipeline = IngestionPipeline()
        
        # Initialize collectors
        self.news_collector = NewsCollector()
        self.trends_collector = TrendsCollector()
        self.youtube_collector = YouTubeCollector()
        self.weather_collector = WeatherCollector()
        self.pricing_collector = PricingCollector()
        self.tax_collector = TaxCollector()
        
        logger.info("DataIngestor initialized")
    
    def generate_batch_id(self) -> str:
        """Generate unique batch ID for tracking"""
        return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def ingest_all_data(self) -> Dict[str, Any]:
        """Ingest data from all sources"""
        batch_id = self.generate_batch_id()
        results = {}
        
        logger.info(f"Starting full data ingestion with batch ID: {batch_id}")
        
        # Ingest news data
        try:
            news_batch = self.news_collector.collect_news()
            news_batch.batch_id = batch_id
            news_result = self.ingestion_pipeline.ingest_news(news_batch)
            results['news'] = news_result
        except Exception as e:
            logger.error(f"Error in news ingestion: {e}")
            results['news'] = {'success': False, 'error': str(e)}
        
        # Ingest trends data
        try:
            trends_batch = self.trends_collector.collect_trends()
            trends_batch.batch_id = batch_id
            trends_result = self.ingestion_pipeline.ingest_trends(trends_batch)
            results['trends'] = trends_result
        except Exception as e:
            logger.error(f"Error in trends ingestion: {e}")
            results['trends'] = {'success': False, 'error': str(e)}
        
        # Ingest YouTube data
        try:
            youtube_batch = self.youtube_collector.collect_youtube_data()
            youtube_batch.batch_id = batch_id
            youtube_result = self.ingestion_pipeline.ingest_youtube(youtube_batch)
            results['youtube'] = youtube_result
        except Exception as e:
            logger.error(f"Error in YouTube ingestion: {e}")
            results['youtube'] = {'success': False, 'error': str(e)}
        
        # Ingest weather data
        try:
            weather_batch = self.weather_collector.collect_weather_data()
            weather_batch.batch_id = batch_id
            weather_result = self.ingestion_pipeline.ingest_weather(weather_batch)
            results['weather'] = weather_result
        except Exception as e:
            logger.error(f"Error in weather ingestion: {e}")
            results['weather'] = {'success': False, 'error': str(e)}
        
        # Ingest pricing data
        try:
            pricing_batch = self.pricing_collector.collect_food_prices()
            pricing_batch.batch_id = batch_id
            pricing_result = self.ingestion_pipeline.ingest_pricing(pricing_batch)
            results['pricing'] = pricing_result
        except Exception as e:
            logger.error(f"Error in pricing ingestion: {e}")
            results['pricing'] = {'success': False, 'error': str(e)}
        
        # Ingest tax data
        try:
            tax_batch = self.tax_collector.collect_tax_revenue()
            tax_batch.batch_id = batch_id
            tax_result = self.ingestion_pipeline.ingest_tax(tax_batch)
            results['tax'] = tax_result
        except Exception as e:
            logger.error(f"Error in tax ingestion: {e}")
            results['tax'] = {'success': False, 'error': str(e)}
        
        # Calculate overall success
        successful_ingestions = sum(1 for result in results.values() if result.get('success'))
        total_sources = len(results)
        
        overall_result = {
            'batch_id': batch_id,
            'timestamp': datetime.now().isoformat(),
            'successful_sources': successful_ingestions,
            'total_sources': total_sources,
            'success_rate': round((successful_ingestions / total_sources) * 100, 2) if total_sources > 0 else 0,
            'details': results
        }
        
        logger.info(f"Data ingestion completed. Success rate: {overall_result['success_rate']}%")
        return overall_result
    
    def ingest_specific_source(self, source: str) -> Dict[str, Any]:
        """Ingest data from a specific source"""
        batch_id = self.generate_batch_id()
        
        logger.info(f"Starting {source} data ingestion with batch ID: {batch_id}")
        
        try:
            if source == 'news':
                batch = self.news_collector.collect_news()
                batch.batch_id = batch_id
                result = self.ingestion_pipeline.ingest_news(batch)
            elif source == 'trends':
                batch = self.trends_collector.collect_trends()
                batch.batch_id = batch_id
                result = self.ingestion_pipeline.ingest_trends(batch)
            elif source == 'youtube':
                batch = self.youtube_collector.collect_youtube_data()
                batch.batch_id = batch_id
                result = self.ingestion_pipeline.ingest_youtube(batch)
            elif source == 'weather':
                batch = self.weather_collector.collect_weather_data()
                batch.batch_id = batch_id
                result = self.ingestion_pipeline.ingest_weather(batch)
            elif source == 'pricing':
                batch = self.pricing_collector.collect_food_prices()
                batch.batch_id = batch_id
                result = self.ingestion_pipeline.ingest_pricing(batch)
            elif source == 'tax':
                batch = self.tax_collector.collect_tax_revenue()
                batch.batch_id = batch_id
                result = self.ingestion_pipeline.ingest_tax(batch)
            else:
                raise ValueError(f"Unknown source: {source}")
            
            result['batch_id'] = batch_id
            result['source'] = source
            result['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"{source} ingestion completed: {result.get('success', False)}")
            return result
            
        except Exception as e:
            logger.error(f"Error in {source} ingestion: {e}")
            return {
                'success': False,
                'error': str(e),
                'batch_id': batch_id,
                'source': source,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_ingestion_status(self) -> Dict[str, Any]:
        """Get current ingestion status and statistics"""
        try:
            stats = self.ingestion_pipeline.get_ingestion_stats()
            
            status = {
                'status': 'operational',
                'last_checked': datetime.now().isoformat(),
                'database_stats': stats,
                'sources_available': ['news', 'trends', 'youtube', 'weather', 'pricing', 'tax']
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting ingestion status: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'last_checked': datetime.now().isoformat()
            }
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up data older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            results = {}
            
            # Clean news
            news_result = self.ingestion_pipeline.news_collection.delete_many({
                'published_at': {'$lt': cutoff_date}
            })
            results['news'] = news_result.deleted_count
            
            # Clean trends
            trends_result = self.ingestion_pipeline.trends_collection.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            results['trends'] = trends_result.deleted_count
            
            # Clean YouTube
            youtube_result = self.ingestion_pipeline.youtube_collection.delete_many({
                'published_at': {'$lt': cutoff_date}
            })
            results['youtube'] = youtube_result.deleted_count
            
            # Clean weather
            weather_result = self.ingestion_pipeline.weather_collection.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            results['weather'] = weather_result.deleted_count
            
            # Clean pricing (keep longer for trend analysis)
            pricing_cutoff = datetime.now() - timedelta(days=days_to_keep * 2)
            pricing_result = self.ingestion_pipeline.pricing_collection.delete_many({
                'date': {'$lt': pricing_cutoff}
            })
            results['pricing'] = pricing_result.deleted_count
            
            # Clean tax (keep longer for historical analysis)
            tax_cutoff = datetime.now() - timedelta(days=days_to_keep * 6)  # 6 months
            tax_result = self.ingestion_pipeline.tax_collection.delete_many({
                'period': {'$lt': tax_cutoff.strftime('%Y-%m')}
            })
            results['tax'] = tax_result.deleted_count
            
            total_deleted = sum(results.values())
            
            logger.info(f"Cleaned up {total_deleted} old records")
            
            return {
                'success': True,
                'deleted_counts': results,
                'total_deleted': total_deleted,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """Close all connections"""
        self.ingestion_pipeline.close()
        logger.info("DataIngestor closed")
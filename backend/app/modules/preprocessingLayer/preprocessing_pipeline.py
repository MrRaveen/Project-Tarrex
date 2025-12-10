import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient

from ...config.mongo_config import get_mongo_client
from .data_cleaner import DataCleaner
from .text_preprocessor import TextPreprocessor
from .normalization_engine import NormalizationEngine

logger = logging.getLogger(__name__)

class PreprocessingPipeline:
    def __init__(self):
        self.data_cleaner = DataCleaner()
        self.text_preprocessor = TextPreprocessor()
        self.normalization_engine = NormalizationEngine()
        
        self.mongo_client = get_mongo_client()
        self.db = self.mongo_client.situational_awareness
        
        # Collections for processed data
        self.processed_news_collection = self.db.processed_news
        self.processed_trends_collection = self.db.processed_trends
        self.processed_youtube_collection = self.db.processed_youtube
        self.processed_weather_collection = self.db.processed_weather
        self.processed_pricing_collection = self.db.processed_pricing
        self.processed_tax_collection = self.db.processed_tax
        
        # Ensure indexes
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure MongoDB indexes for processed data"""
        # Processed news indexes
        self.processed_news_collection.create_index([("processed_at", -1)])
        self.processed_news_collection.create_index([("source", 1)])
        self.processed_news_collection.create_index([("sentiment", 1)])
        self.processed_news_collection.create_index([("keywords", 1)])
        
        # Processed trends indexes
        self.processed_trends_collection.create_index([("processed_at", -1)])
        self.processed_trends_collection.create_index([("keyword", 1)])
        self.processed_trends_collection.create_index([("normalized_interest", 1)])
        
        # Processed YouTube indexes
        self.processed_youtube_collection.create_index([("processed_at", -1)])
        self.processed_youtube_collection.create_index([("channel_id", 1)])
        self.processed_youtube_collection.create_index([("sentiment", 1)])
        
        # Processed weather indexes
        self.processed_weather_collection.create_index([("processed_at", -1)])
        self.processed_weather_collection.create_index([("location", 1)])
        self.processed_weather_collection.create_index([("normalized_temperature", 1)])
        
        # Processed pricing indexes
        self.processed_pricing_collection.create_index([("processed_at", -1)])
        self.processed_pricing_collection.create_index([("market", 1)])
        self.processed_pricing_collection.create_index([("normalized_price", 1)])
        
        # Processed tax indexes
        self.processed_tax_collection.create_index([("processed_at", -1)])
        self.processed_tax_collection.create_index([("source", 1)])
        self.processed_tax_collection.create_index([("normalized_revenue", 1)])
        
        logger.info("Processed data indexes ensured")
    
    def preprocess_news(self, news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess news articles"""
        processed_news = []
        
        for news in news_data:
            try:
                # Clean text
                cleaned_title = self.data_cleaner.clean_text(news.get('title', ''))
                cleaned_content = self.data_cleaner.clean_text(news.get('content', ''))
                cleaned_summary = self.data_cleaner.clean_text(news.get('summary', ''))
                
                # Extract keywords
                combined_text = f"{cleaned_title} {cleaned_content}"
                keywords = self.text_preprocessor.extract_keywords(combined_text)
                
                # Sentiment analysis
                sentiment = self.text_preprocessor.detect_sentiment(combined_text)
                
                # Named entity recognition
                entities = self.text_preprocessor.extract_named_entities(combined_text)
                
                # Readability score
                readability = self.text_preprocessor.calculate_readability_score(cleaned_content)
                
                # Language detection
                language = self.text_preprocessor.detect_language(combined_text)
                
                # Normalize location
                location = self.data_cleaner.normalize_location(news.get('location', ''))
                
                # Create processed news document
                processed_news.append({
                    'original_id': news.get('_id'),
                    'title': cleaned_title,
                    'content': cleaned_content,
                    'summary': cleaned_summary,
                    'source': news.get('source'),
                    'published_at': news.get('published_at'),
                    'location': location,
                    'language': language,
                    'keywords': keywords,
                    'sentiment': sentiment,
                    'entities': entities,
                    'readability_score': readability,
                    'processed_at': datetime.now(),
                    'metadata': {
                        'original_url': news.get('url'),
                        'category': news.get('category'),
                        'author': news.get('author'),
                        'word_count': len(cleaned_content.split()),
                        'character_count': len(cleaned_content)
                    }
                })
                
            except Exception as e:
                logger.error(f"Error preprocessing news: {e}")
                continue
        
        return processed_news
    
    def preprocess_trends(self, trends_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess trends data"""
        processed_trends = []
        
        for trend in trends_data:
            try:
                # Clean keyword
                keyword = self.data_cleaner.clean_text(trend.get('keyword', ''))
                
                # Normalize interest value
                interest = trend.get('interest', 0)
                normalized_interest = self.normalization_engine.min_max_normalize(
                    interest, 0, 100
                )
                
                # Detect sentiment from keyword
                sentiment = self.text_preprocessor.detect_sentiment(keyword)
                
                processed_trends.append({
                    'original_id': trend.get('_id'),
                    'keyword': keyword,
                    'interest': interest,
                    'normalized_interest': normalized_interest,
                    'region': trend.get('region'),
                    'timestamp': trend.get('timestamp'),
                    'sentiment': sentiment,
                    'processed_at': datetime.now(),
                    'metadata': {
                        'geo_code': trend.get('geo_code'),
                        'time_range': trend.get('time_range'),
                        'category': trend.get('category')
                    }
                })
                
            except Exception as e:
                logger.error(f"Error preprocessing trend: {e}")
                continue
        
        return processed_trends
    
    def preprocess_youtube(self, youtube_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess YouTube data"""
        processed_videos = []
        
        for video in youtube_data:
            try:
                # Clean text
                cleaned_title = self.data_cleaner.clean_text(video.get('title', ''))
                cleaned_description = self.data_cleaner.clean_text(video.get('description', ''))
                
                # Extract keywords
                combined_text = f"{cleaned_title} {cleaned_description}"
                keywords = self.text_preprocessor.extract_keywords(combined_text)
                
                # Sentiment analysis
                sentiment = self.text_preprocessor.detect_sentiment(combined_text)
                
                # Named entity recognition
                entities = self.text_preprocessor.extract_named_entities(combined_text)
                
                # Normalize engagement metrics
                views = video.get('view_count', 0)
                likes = video.get('like_count', 0)
                comments = video.get('comment_count', 0)
                
                engagement_score = self._calculate_engagement_score(views, likes, comments)
                
                processed_videos.append({
                    'original_id': video.get('_id'),
                    'video_id': video.get('video_id'),
                    'title': cleaned_title,
                    'description': cleaned_description,
                    'channel_id': video.get('channel_id'),
                    'channel_title': video.get('channel_title'),
                    'published_at': video.get('published_at'),
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'engagement_score': engagement_score,
                    'keywords': keywords,
                    'sentiment': sentiment,
                    'entities': entities,
                    'processed_at': datetime.now(),
                    'metadata': {
                        'duration': video.get('duration'),
                        'thumbnail_url': video.get('thumbnail_url'),
                        'category_id': video.get('category_id')
                    }
                })
                
            except Exception as e:
                logger.error(f"Error preprocessing YouTube video: {e}")
                continue
        
        return processed_videos
    
    def _calculate_engagement_score(self, views: int, likes: int, comments: int) -> float:
        """Calculate engagement score for YouTube videos"""
        if views == 0:
            return 0.0
        
        like_ratio = likes / views
        comment_ratio = comments / views
        
        # Weighted engagement score
        engagement = (like_ratio * 0.6) + (comment_ratio * 0.4)
        
        return min(1.0, engagement * 100)  # Scale to 0-1 range
    
    def preprocess_weather(self, weather_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess weather data"""
        processed_weather = []
        
        for weather in weather_data:
            try:
                # Normalize location
                location = self.data_cleaner.normalize_location(weather.get('location_name', ''))
                
                # Normalize temperature
                temperature = weather.get('temperature', 0)
                normalized_temp = self.normalization_engine.normalize_weather_data('temperature', temperature)
                
                # Normalize humidity
                humidity = weather.get('humidity', 0)
                normalized_humidity = self.normalization_engine.normalize_weather_data('humidity', humidity)
                
                processed_weather.append({
                    'original_id': weather.get('_id'),
                    'location': location,
                    'latitude': weather.get('latitude'),
                    'longitude': weather.get('longitude'),
                    'temperature': temperature,
                    'normalized_temperature': normalized_temp['normalized'],
                    'humidity': humidity,
                    'normalized_humidity': normalized_humidity['normalized'],
                    'weather_condition': weather.get('weather_condition'),
                    'wind_speed': weather.get('wind_speed'),
                    'timestamp': weather.get('timestamp'),
                    'processed_at': datetime.now(),
                    'metadata': {
                        'pressure': weather.get('pressure'),
                        'visibility': weather.get('visibility'),
                        'cloud_cover': weather.get('cloud_cover'),
                        'uv_index': weather.get('uv_index')
                    }
                })
                
            except Exception as e:
                logger.error(f"Error preprocessing weather data: {e}")
                continue
        
        return processed_weather
    
    def preprocess_pricing(self, pricing_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess pricing data"""
        processed_pricing = []
        
        for price_record in pricing_data:
            try:
                # Extract all prices for normalization
                all_prices = []
                for price_item in price_record.get('prices', []):
                    if isinstance(price_item, dict):
                        all_prices.append(price_item.get('price', 0))
                
                # Normalize prices
                price_normalization = self.normalization_engine.normalize_price_data(all_prices)
                
                # Normalize location
                location = self.data_cleaner.normalize_location(price_record.get('location', ''))
                
                processed_pricing.append({
                    'original_id': price_record.get('_id'),
                    'date': price_record.get('date'),
                    'location': location,
                    'market': price_record.get('market'),
                    'average_price': price_record.get('average_price'),
                    'price_change': price_record.get('price_change'),
                    'normalized_prices': price_normalization['normalized_prices'],
                    'price_stats': price_normalization['stats'],
                    'processed_at': datetime.now(),
                    'metadata': {
                        'source': price_record.get('source'),
                        'items_count': len(price_record.get('prices', [])),
                        'price_volatility': price_normalization['stats'].get('std_dev', 0)
                    }
                })
                
            except Exception as e:
                logger.error(f"Error preprocessing pricing data: {e}")
                continue
        
        return processed_pricing
    
    def preprocess_tax(self, tax_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Preprocess tax revenue data"""
        processed_tax = []
        
        for tax_record in tax_data:
            try:
                # Normalize revenue
                total_revenue = tax_record.get('total_revenue', 0)
                normalized_revenue = self.normalization_engine.min_max_normalize(total_revenue, 0, 1000000)
                
                # Normalize growth rate
                growth_rate = tax_record.get('growth_rate', 0)
                normalized_growth = self.normalization_engine.min_max_normalize(growth_rate, -20, 20)
                
                processed_tax.append({
                    'original_id': tax_record.get('_id'),
                    'period': tax_record.get('period'),
                    'period_type': tax_record.get('period_type'),
                    'source': tax_record.get('source'),
                    'total_revenue': total_revenue,
                    'normalized_revenue': normalized_revenue,
                    'growth_rate': growth_rate,
                    'normalized_growth': normalized_growth,
                    'target_achievement': tax_record.get('target_achievement'),
                    'processed_at': datetime.now(),
                    'metadata': {
                        'currency': tax_record.get('metadata', {}).get('currency'),
                        'fiscal_year': tax_record.get('metadata', {}).get('fiscal_year'),
                        'categories_count': len(tax_record.get('categories', []))
                    }
                })
                
            except Exception as e:
                logger.error(f"Error preprocessing tax data: {e}")
                continue
        
        return processed_tax
    
    def run_full_preprocessing(self) -> Dict[str, Any]:
        """Run preprocessing for all data types"""
        results = {}
        
        logger.info("Starting full preprocessing pipeline...")
        
        # Preprocess each data type
        data_types = ['news', 'trends', 'youtube', 'weather', 'pricing', 'tax']
        
        for data_type in data_types:
            try:
                # Get raw data from MongoDB
                raw_collection = getattr(self.db, data_type)
                raw_data = list(raw_collection.find().limit(1000))  # Limit for demo
                
                if not raw_data:
                    results[data_type] = {
                        'processed_count': 0,
                        'status': 'no_data'
                    }
                    continue
                
                # Preprocess data
                if data_type == 'news':
                    processed_data = self.preprocess_news(raw_data)
                elif data_type == 'trends':
                    processed_data = self.preprocess_trends(raw_data)
                elif data_type == 'youtube':
                    processed_data = self.preprocess_youtube(raw_data)
                elif data_type == 'weather':
                    processed_data = self.preprocess_weather(raw_data)
                elif data_type == 'pricing':
                    processed_data = self.preprocess_pricing(raw_data)
                elif data_type == 'tax':
                    processed_data = self.preprocess_tax(raw_data)
                else:
                    continue
                
                # Store processed data
                processed_collection = getattr(self, f'processed_{data_type}_collection')
                if processed_data:
                    processed_collection.insert_many(processed_data)
                
                results[data_type] = {
                    'processed_count': len(processed_data),
                    'raw_count': len(raw_data),
                    'status': 'success'
                }
                
                logger.info(f"Preprocessed {len(processed_data)} {data_type} records")
                
            except Exception as e:
                logger.error(f"Error preprocessing {data_type}: {e}")
                results[data_type] = {
                    'processed_count': 0,
                    'status': 'error',
                    'error': str(e)
                }
        
        # Calculate overall statistics
        total_processed = sum(result.get('processed_count', 0) for result in results.values())
        
        return {
            'overall_status': 'completed',
            'total_processed': total_processed,
            'timestamp': datetime.now().isoformat(),
            'details': results
        }
    
    def get_preprocessing_stats(self) -> Dict[str, Any]:
        """Get preprocessing statistics"""
        stats = {}
        
        data_types = ['news', 'trends', 'youtube', 'weather', 'pricing', 'tax']
        
        for data_type in data_types:
            try:
                processed_collection = getattr(self, f'processed_{data_type}_collection')
                count = processed_collection.count_documents({})
                stats[data_type] = count
            except Exception as e:
                logger.error(f"Error getting stats for {data_type}: {e}")
                stats[data_type] = 0
        
        return {
            'processed_counts': stats,
            'last_updated': datetime.now().isoformat()
        }
    
    def close(self):
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")
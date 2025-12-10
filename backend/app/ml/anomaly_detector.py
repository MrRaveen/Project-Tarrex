import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from app.config.mongo_config import get_database
import logging
from datetime import datetime, timedelta
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Anomaly detection for situational awareness data"""
    
    def __init__(self):
        self.db = get_database()
    
    def detect_weather_anomalies(self, lookback_days: int = 30) -> Dict:
        """Detect anomalies in weather data"""
        try:
            collection = self.db['weather_data']
            
            # Get recent weather data
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            weather_data = list(collection.find({
                'timestamp': {'$gte': cutoff_date}
            }).sort('timestamp', 1))
            
            if not weather_data:
                return {'anomalies': [], 'summary': 'No weather data available'}
            
            df = pd.DataFrame(weather_data)
            
            # Detect anomalies in key metrics
            anomalies = []
            metrics = ['temperature', 'humidity', 'pressure', 'wind_speed']
            
            for metric in metrics:
                if metric in df.columns:
                    metric_anomalies = self._detect_univariate_anomalies(df, metric)
                    anomalies.extend(metric_anomalies)
            
            # Detect multivariate anomalies
            multivariate_anomalies = self._detect_multivariate_anomalies(df, metrics)
            anomalies.extend(multivariate_anomalies)
            
            return {
                'anomalies': anomalies,
                'summary': f"Detected {len(anomalies)} weather anomalies",
                'period': f"Last {lookback_days} days"
            }
            
        except Exception as e:
            logger.error(f"Error detecting weather anomalies: {str(e)}")
            return {'anomalies': [], 'summary': f'Error: {str(e)}'}
    
    def detect_pricing_anomalies(self, lookback_days: int = 30) -> Dict:
        """Detect anomalies in food pricing data"""
        try:
            collection = self.db['food_prices']
            
            # Get recent pricing data
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            pricing_data = list(collection.find({
                'timestamp': {'$gte': cutoff_date}
            }).sort('timestamp', 1))
            
            if not pricing_data:
                return {'anomalies': [], 'summary': 'No pricing data available'}
            
            df = pd.DataFrame(pricing_data)
            
            # Group by item and detect anomalies
            anomalies = []
            
            if 'item' in df.columns and 'price' in df.columns:
                for item in df['item'].unique():
                    item_data = df[df['item'] == item]
                    if len(item_data) > 10:  # Need sufficient data
                        item_anomalies = self._detect_price_anomalies(item_data, item)
                        anomalies.extend(item_anomalies)
            
            return {
                'anomalies': anomalies,
                'summary': f"Detected {len(anomalies)} pricing anomalies",
                'period': f"Last {lookback_days} days"
            }
            
        except Exception as e:
            logger.error(f"Error detecting pricing anomalies: {str(e)}")
            return {'anomalies': [], 'summary': f'Error: {str(e)}'}
    
    def detect_tax_anomalies(self, lookback_months: int = 12) -> Dict:
        """Detect anomalies in tax revenue data"""
        try:
            collection = self.db['tax_revenues']
            
            # Get tax data
            cutoff_date = datetime.now() - timedelta(days=lookback_months * 30)
            tax_data = list(collection.find({
                'timestamp': {'$gte': cutoff_date}
            }).sort('timestamp', 1))
            
            if not tax_data:
                return {'anomalies': [], 'summary': 'No tax data available'}
            
            df = pd.DataFrame(tax_data)
            
            # Detect anomalies in revenue
            anomalies = []
            
            if 'amount' in df.columns:
                revenue_anomalies = self._detect_revenue_anomalies(df, 'amount')
                anomalies.extend(revenue_anomalies)
            
            return {
                'anomalies': anomalies,
                'summary': f"Detected {len(anomalies)} tax anomalies",
                'period': f"Last {lookback_months} months"
            }
            
        except Exception as e:
            logger.error(f"Error detecting tax anomalies: {str(e)}")
            return {'anomalies': [], 'summary': f'Error: {str(e)}'}
    
    def detect_news_sentiment_anomalies(self, lookback_days: int = 7) -> Dict:
        """Detect anomalies in news sentiment"""
        try:
            collection = self.db['processed_news']
            
            # Get recent news data
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            news_data = list(collection.find({
                'timestamp': {'$gte': cutoff_date},
                'sentiment_score': {'$exists': True}
            }).sort('timestamp', 1))
            
            if not news_data:
                return {'anomalies': [], 'summary': 'No news sentiment data available'}
            
            df = pd.DataFrame(news_data)
            
            # Detect sentiment anomalies
            anomalies = []
            
            if 'sentiment_score' in df.columns:
                sentiment_anomalies = self._detect_sentiment_anomalies(df, 'sentiment_score')
                anomalies.extend(sentiment_anomalies)
            
            return {
                'anomalies': anomalies,
                'summary': f"Detected {len(anomalies)} sentiment anomalies",
                'period': f"Last {lookback_days} days"
            }
            
        except Exception as e:
            logger.error(f"Error detecting sentiment anomalies: {str(e)}")
            return {'anomalies': [], 'summary': f'Error: {str(e)}'}
    
    def detect_youtube_engagement_anomalies(self, lookback_days: int = 7) -> Dict:
        """Detect anomalies in YouTube engagement metrics"""
        try:
            collection = self.db['youtube_videos']
            
            # Get recent YouTube data
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            youtube_data = list(collection.find({
                'published_at': {'$gte': cutoff_date}
            }).sort('published_at', 1))
            
            if not youtube_data:
                return {'anomalies': [], 'summary': 'No YouTube data available'}
            
            df = pd.DataFrame(youtube_data)
            
            # Detect engagement anomalies
            anomalies = []
            engagement_metrics = ['view_count', 'like_count', 'comment_count']
            
            for metric in engagement_metrics:
                if metric in df.columns:
                    metric_anomalies = self._detect_engagement_anomalies(df, metric)
                    anomalies.extend(metric_anomalies)
            
            return {
                'anomalies': anomalies,
                'summary': f"Detected {len(anomalies)} engagement anomalies",
                'period': f"Last {lookback_days} days"
            }
            
        except Exception as e:
            logger.error(f"Error detecting YouTube anomalies: {str(e)}")
            return {'anomalies': [], 'summary': f'Error: {str(e)}'}
    
    def _detect_univariate_anomalies(self, df: pd.DataFrame, column: str, 
                                  method: str = 'zscore', threshold: float = 3.0) -> List[Dict]:
        """Detect univariate anomalies using statistical methods"""
        anomalies = []
        
        if column not in df.columns or df[column].isna().all():
            return anomalies
        
        valid_data = df[column].dropna()
        
        if len(valid_data) < 10:  # Need sufficient data
            return anomalies
        
        if method == 'zscore':
            # Z-score method
            z_scores = np.abs(stats.zscore(valid_data))
            anomaly_indices = np.where(z_scores > threshold)[0]
            
            for idx in anomaly_indices:
                original_idx = valid_data.index[idx]
                anomalies.append({
                    'type': 'univariate',
                    'metric': column,
                    'value': df.loc[original_idx, column],
                    'z_score': z_scores[idx],
                    'timestamp': df.loc[original_idx, 'timestamp'] if 'timestamp' in df.columns else None,
                    'method': 'zscore',
                    'threshold': threshold
                })
        
        elif method == 'iqr':
            # IQR method
            Q1 = valid_data.quantile(0.25)
            Q3 = valid_data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            anomaly_mask = (valid_data < lower_bound) | (valid_data > upper_bound)
            anomaly_indices = valid_data.index[anomaly_mask]
            
            for idx in anomaly_indices:
                anomalies.append({
                    'type': 'univariate',
                    'metric': column,
                    'value': df.loc[idx, column],
                    'bounds': {'lower': lower_bound, 'upper': upper_bound},
                    'timestamp': df.loc[idx, 'timestamp'] if 'timestamp' in df.columns else None,
                    'method': 'iqr'
                })
        
        return anomalies
    
    def _detect_multivariate_anomalies(self, df: pd.DataFrame, columns: List[str], 
                                    contamination: float = 0.1) -> List[Dict]:
        """Detect multivariate anomalies using Isolation Forest"""
        anomalies = []
        
        # Filter to only include specified columns that exist and have data
        valid_columns = [col for col in columns if col in df.columns and not df[col].isna().all()]
        
        if len(valid_columns) < 2 or len(df) < 20:
            return anomalies
        
        # Prepare data
        X = df[valid_columns].copy()
        X = X.dropna()
        
        if len(X) < 10:
            return anomalies
        
        # Scale the data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Use Isolation Forest for anomaly detection
        clf = IsolationForest(contamination=contamination, random_state=42)
        predictions = clf.fit_predict(X_scaled)
        
        # Get anomaly indices
        anomaly_indices = X.index[predictions == -1]
        
        for idx in anomaly_indices:
            anomaly_data = {
                'type': 'multivariate',
                'metrics': valid_columns,
                'values': {col: df.loc[idx, col] for col in valid_columns},
                'timestamp': df.loc[idx, 'timestamp'] if 'timestamp' in df.columns else None,
                'method': 'isolation_forest',
                'contamination': contamination
            }
            anomalies.append(anomaly_data)
        
        return anomalies
    
    def _detect_price_anomalies(self, df: pd.DataFrame, item: str) -> List[Dict]:
        """Detect anomalies in price data for specific items"""
        anomalies = []
        
        if 'price' not in df.columns or 'timestamp' not in df.columns:
            return anomalies
        
        # Calculate price changes and detect anomalies
        df = df.sort_values('timestamp')
        df['price_change'] = df['price'].pct_change()
        
        # Detect large price changes
        large_changes = df[np.abs(df['price_change']) > 0.5]  # 50% change
        
        for _, row in large_changes.iterrows():
            anomalies.append({
                'type': 'price_change',
                'item': item,
                'price': row['price'],
                'price_change': row['price_change'],
                'timestamp': row['timestamp'],
                'location': row.get('location', 'unknown'),
                'severity': 'high' if abs(row['price_change']) > 1.0 else 'medium'
            })
        
        # Also detect statistical outliers
        statistical_anomalies = self._detect_univariate_anomalies(df, 'price', 'iqr')
        for anomaly in statistical_anomalies:
            anomaly['item'] = item
            anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_revenue_anomalies(self, df: pd.DataFrame, revenue_col: str) -> List[Dict]:
        """Detect anomalies in revenue data"""
        anomalies = []
        
        if revenue_col not in df.columns or 'timestamp' not in df.columns:
            return anomalies
        
        df = df.sort_values('timestamp')
        
        # Detect significant revenue drops or spikes
        df['revenue_change'] = df[revenue_col].pct_change()
        
        significant_changes = df[np.abs(df['revenue_change']) > 0.3]  # 30% change
        
        for _, row in significant_changes.iterrows():
            anomalies.append({
                'type': 'revenue_change',
                'revenue': row[revenue_col],
                'revenue_change': row['revenue_change'],
                'timestamp': row['timestamp'],
                'tax_type': row.get('tax_type', 'unknown'),
                'severity': 'high' if abs(row['revenue_change']) > 0.5 else 'medium'
            })
        
        return anomalies
    
    def _detect_sentiment_anomalies(self, df: pd.DataFrame, sentiment_col: str) -> List[Dict]:
        """Detect anomalies in sentiment data"""
        anomalies = []
        
        if sentiment_col not in df.columns:
            return anomalies
        
        # Detect extreme sentiment values
        extreme_sentiment = df[(df[sentiment_col] < -0.8) | (df[sentiment_col] > 0.8)]
        
        for _, row in extreme_sentiment.iterrows():
            anomalies.append({
                'type': 'sentiment_extreme',
                'sentiment_score': row[sentiment_col],
                'title': row.get('title', 'Unknown'),
                'timestamp': row.get('timestamp'),
                'source': row.get('source', 'unknown'),
                'severity': 'high' if abs(row[sentiment_col]) > 0.9 else 'medium'
            })
        
        # Detect sentiment spikes
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
            df['sentiment_change'] = df[sentiment_col].diff().abs()
            
            sentiment_spikes = df[df['sentiment_change'] > 0.5]
            
            for _, row in sentiment_spikes.iterrows():
                anomalies.append({
                    'type': 'sentiment_spike',
                    'sentiment_score': row[sentiment_col],
                    'sentiment_change': row['sentiment_change'],
                    'title': row.get('title', 'Unknown'),
                    'timestamp': row['timestamp'],
                    'source': row.get('source', 'unknown'),
                    'severity': 'high' if row['sentiment_change'] > 0.7 else 'medium'
                })
        
        return anomalies
    
    def _detect_engagement_anomalies(self, df: pd.DataFrame, engagement_col: str) -> List[Dict]:
        """Detect anomalies in engagement metrics"""
        anomalies = []
        
        if engagement_col not in df.columns:
            return anomalies
        
        # Detect unusually high engagement
        Q3 = df[engagement_col].quantile(0.75)
        IQR = df[engagement_col].quantile(0.75) - df[engagement_col].quantile(0.25)
        upper_bound = Q3 + 3 * IQR
        
        high_engagement = df[df[engagement_col] > upper_bound]
        
        for _, row in high_engagement.iterrows():
            anomalies.append({
                'type': 'high_engagement',
                'metric': engagement_col,
                'value': row[engagement_col],
                'upper_bound': upper_bound,
                'title': row.get('title', 'Unknown'),
                'published_at': row.get('published_at'),
                'video_id': row.get('video_id', 'unknown'),
                'severity': 'high'
            })
        
        return anomalies
    
    def save_anomalies_to_mongodb(self, anomalies: List[Dict], anomaly_type: str):
        """Save detected anomalies to MongoDB"""
        try:
            collection = self.db['detected_anomalies']
            
            if anomalies:
                # Add metadata to each anomaly
                for anomaly in anomalies:
                    anomaly['detected_at'] = datetime.now()
                    anomaly['anomaly_type'] = anomaly_type
                    anomaly['processed'] = False
                
                # Insert anomalies
                result = collection.insert_many(anomalies)
                logger.info(f"Saved {len(result.inserted_ids)} {anomaly_type} anomalies")
                
                # Create indexes
                collection.create_index('timestamp')
                collection.create_index('anomaly_type')
                collection.create_index('severity')
                
        except Exception as e:
            logger.error(f"Error saving anomalies to MongoDB: {str(e)}")
            raise
    
    def get_recent_anomalies(self, hours: int = 24, anomaly_type: Optional[str] = None) -> List[Dict]:
        """Get recent anomalies from MongoDB"""
        try:
            collection = self.db['detected_anomalies']
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = {'detected_at': {'$gte': cutoff_time}}
            if anomaly_type:
                query['anomaly_type'] = anomaly_type
            
            anomalies = list(collection.find(query).sort('detected_at', -1))
            return anomalies
            
        except Exception as e:
            logger.error(f"Error retrieving anomalies: {str(e)}")
            return []
    
    def calculate_anomaly_score(self, data_point: Dict, context: Dict) -> float:
        """Calculate an anomaly score for a data point given context"""
        score = 0.0
        
        # Implement scoring logic based on data type and context
        if 'temperature' in data_point:
            temp = data_point['temperature']
            # Sri Lanka context: normal range ~25-35°C
            if temp < 20 or temp > 38:
                score += 0.7
            elif temp < 15 or temp > 40:
                score += 0.9
        
        if 'price' in data_point and 'item' in data_point:
            price = data_point['price']
            item = data_point['item']
            # Add price-based scoring logic
            pass
        
        # Add more scoring rules based on different metrics
        
        return min(score, 1.0)  # Cap at 1.0
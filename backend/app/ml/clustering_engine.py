import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
from app.config.mongo_config import get_database
import logging
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

logger = logging.getLogger(__name__)

class ClusteringEngine:
    def __init__(self):
        self.db = get_database()
        self.scaler = StandardScaler()
        
        # Sri Lankan context stopwords
        self.sl_stopwords = set(stopwords.words('english'))
        self.sl_stopwords.update([
            'sri', 'lanka', 'lankan', 'colombo', 'government', 'minister', 
            'president', 'said', 'says', 'today', 'yesterday', 'week'
        ])
    
    def cluster_news_articles(self, lookback_days: int = 30, max_clusters: int = 10) -> Dict:
        """Cluster news articles using text and metadata features"""
        try:
            collection = self.db['processed_news_data']
            
            # Get recent news articles
            start_date = datetime.now() - timedelta(days=lookback_days)
            query = {
                'timestamp': {'$gte': start_date},
                'content': {'$exists': True, '$ne': ''}
            }
            
            news_articles = list(collection.find(query))
            
            if len(news_articles) < 5:
                return {"status": "insufficient_data", "clusters": [], "article_count": len(news_articles)}
            
            # Prepare data for clustering
            df = pd.DataFrame(news_articles)
            
            # Text vectorization
            tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=list(self.sl_stopwords),
                ngram_range=(1, 2)
            )
            
            # Combine title and content for better clustering
            texts = df.apply(lambda x: f"{x.get('title', '')} {x.get('content', '')}", axis=1)
            text_features = tfidf_vectorizer.fit_transform(texts).toarray()
            
            # Additional features
            additional_features = []
            for article in news_articles:
                features = [
                    article.get('sentiment_score', 0),
                    len(article.get('content', '')) / 1000,  # Normalized content length
                    1 if article.get('category') == 'politics' else 0,
                    1 if article.get('category') == 'economy' else 0,
                    1 if article.get('category') == 'weather' else 0
                ]
                additional_features.append(features)
            
            additional_features = np.array(additional_features)
            
            # Combine features
            if len(additional_features) > 0:
                all_features = np.hstack([text_features, additional_features])
            else:
                all_features = text_features
            
            # Determine optimal number of clusters
            optimal_clusters = self._determine_optimal_clusters(all_features, max_clusters)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(all_features)
            
            # Calculate cluster quality
            silhouette_avg = silhouette_score(all_features, cluster_labels) if optimal_clusters > 1 else 0
            
            # Create cluster summaries
            clusters = self._create_news_cluster_summaries(df, cluster_labels, tfidf_vectorizer)
            
            return {
                "status": "success",
                "clusters": clusters,
                "cluster_count": optimal_clusters,
                "silhouette_score": round(silhouette_avg, 3),
                "article_count": len(news_articles),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error clustering news articles: {str(e)}")
            return {"status": "error", "error": str(e), "clusters": []}
    
    def cluster_youtube_videos(self, lookback_days: int = 30, max_clusters: int = 8) -> Dict:
        """Cluster YouTube videos based on engagement and content"""
        try:
            collection = self.db['processed_youtube_data']
            
            # Get recent YouTube videos
            start_date = datetime.now() - timedelta(days=lookback_days)
            query = {
                'timestamp': {'$gte': start_date},
                'title': {'$exists': True}
            }
            
            youtube_videos = list(collection.find(query))
            
            if len(youtube_videos) < 5:
                return {"status": "insufficient_data", "clusters": [], "video_count": len(youtube_videos)}
            
            # Prepare data for clustering
            df = pd.DataFrame(youtube_videos)
            
            # Text vectorization for titles
            tfidf_vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words=list(self.sl_stopwords),
                ngram_range=(1, 2)
            )
            
            titles = df['title'].fillna('')
            text_features = tfidf_vectorizer.fit_transform(titles).toarray()
            
            # Engagement features
            engagement_features = []
            for video in youtube_videos:
                features = [
                    video.get('view_count', 0) / 1000,  # Normalized
                    video.get('like_count', 0) / 100,
                    video.get('comment_count', 0) / 50,
                    video.get('engagement_score', 0)
                ]
                engagement_features.append(features)
            
            engagement_features = np.array(engagement_features)
            
            # Combine features
            all_features = np.hstack([text_features, engagement_features])
            
            # Determine optimal number of clusters
            optimal_clusters = self._determine_optimal_clusters(all_features, max_clusters)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(all_features)
            
            # Calculate cluster quality
            silhouette_avg = silhouette_score(all_features, cluster_labels) if optimal_clusters > 1 else 0
            
            # Create cluster summaries
            clusters = self._create_youtube_cluster_summaries(df, cluster_labels, tfidf_vectorizer)
            
            return {
                "status": "success",
                "clusters": clusters,
                "cluster_count": optimal_clusters,
                "silhouette_score": round(silhouette_avg, 3),
                "video_count": len(youtube_videos),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error clustering YouTube videos: {str(e)}")
            return {"status": "error", "error": str(e), "clusters": []}
    
    def cluster_food_prices(self, lookback_days: int = 90, max_clusters: int = 6) -> Dict:
        """Cluster food prices based on temporal patterns"""
        try:
            collection = self.db['processed_food_prices']
            
            # Get recent price data
            start_date = datetime.now() - timedelta(days=lookback_days)
            query = {
                'timestamp': {'$gte': start_date},
                'price': {'$exists': True}
            }
            
            price_data = list(collection.find(query))
            
            if len(price_data) < 10:
                return {"status": "insufficient_data", "clusters": [], "data_point_count": len(price_data)}
            
            # Prepare data for clustering
            df = pd.DataFrame(price_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Group by commodity and create time series features
            commodity_features = []
            commodities = df['commodity'].unique()
            
            for commodity in commodities:
                commodity_data = df[df['commodity'] == commodity]
                if len(commodity_data) >= 7:  # Minimum 7 days of data
                    features = self._extract_price_time_series_features(commodity_data)
                    features['commodity'] = commodity
                    commodity_features.append(features)
            
            if len(commodity_features) < 3:
                return {"status": "insufficient_data", "clusters": [], "commodity_count": len(commodity_features)}
            
            feature_df = pd.DataFrame(commodity_features)
            numeric_cols = feature_df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                return {"status": "no_numeric_features", "clusters": []}
            
            # Scale features
            X = feature_df[numeric_cols].fillna(0)
            X_scaled = self.scaler.fit_transform(X)
            
            # Determine optimal number of clusters
            optimal_clusters = self._determine_optimal_clusters(X_scaled, max_clusters)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            # Calculate cluster quality
            silhouette_avg = silhouette_score(X_scaled, cluster_labels) if optimal_clusters > 1 else 0
            
            # Create cluster summaries
            clusters = self._create_price_cluster_summaries(feature_df, cluster_labels, commodities)
            
            return {
                "status": "success",
                "clusters": clusters,
                "cluster_count": optimal_clusters,
                "silhouette_score": round(silhouette_avg, 3),
                "commodity_count": len(commodities),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error clustering food prices: {str(e)}")
            return {"status": "error", "error": str(e), "clusters": []}
    
    def _determine_optimal_clusters(self, data: np.ndarray, max_clusters: int) -> int:
        """Determine optimal number of clusters using elbow method and silhouette score"""
        if len(data) <= 3:
            return min(2, len(data))
        
        max_clusters = min(max_clusters, len(data) - 1)
        
        if max_clusters <= 1:
            return 1
        
        # Use simplified approach for efficiency
        silhouette_scores = []
        
        for n_clusters in range(2, max_clusters + 1):
            if n_clusters >= len(data):
                break
                
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(data)
            
            if len(set(cluster_labels)) > 1:
                score = silhouette_score(data, cluster_labels)
                silhouette_scores.append(score)
            else:
                silhouette_scores.append(0)
        
        if not silhouette_scores:
            return 2
        
        # Return cluster count with highest silhouette score
        optimal_clusters = np.argmax(silhouette_scores) + 2  # +2 because we started from 2 clusters
        return min(optimal_clusters, max_clusters)
    
    def _extract_price_time_series_features(self, price_data: pd.DataFrame) -> Dict:
        """Extract features from price time series"""
        prices = price_data['price'].values
        
        features = {
            'mean_price': np.mean(prices),
            'price_std': np.std(prices),
            'price_variance': np.var(prices),
            'price_range': np.max(prices) - np.min(prices),
            'trend_slope': self._calculate_trend_slope(prices),
            'volatility': np.std(prices) / np.mean(prices) if np.mean(prices) != 0 else 0,
            'recent_change': (prices[-1] - prices[0]) / prices[0] if prices[0] != 0 else 0
        }
        
        return features
    
    def _calculate_trend_slope(self, values: np.ndarray) -> float:
        """Calculate linear trend slope"""
        if len(values) < 2:
            return 0
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return slope / np.mean(values) if np.mean(values) != 0 else slope
    
    def _create_news_cluster_summaries(self, df: pd.DataFrame, cluster_labels: np.ndarray, 
                                     vectorizer: TfidfVectorizer) -> List[Dict]:
        """Create human-readable summaries for news clusters"""
        clusters = []
        
        for cluster_id in range(max(cluster_labels) + 1):
            cluster_mask = cluster_labels == cluster_id
            cluster_articles = df[cluster_mask]
            
            if len(cluster_articles) == 0:
                continue
            
            # Get top keywords
            cluster_texts = cluster_articles.apply(
                lambda x: f"{x.get('title', '')} {x.get('content', '')}", axis=1
            )
            
            tfidf_matrix = vectorizer.transform(cluster_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top keywords by average TF-IDF
            tfidf_sums = np.array(tfidf_matrix.sum(axis=0)).flatten()
            top_keyword_indices = tfidf_sums.argsort()[-5:][::-1]
            top_keywords = [feature_names[i] for i in top_keyword_indices if tfidf_sums[i] > 0]
            
            # Cluster statistics
            avg_sentiment = cluster_articles['sentiment_score'].mean() if 'sentiment_score' in cluster_articles.columns else 0
            
            clusters.append({
                "cluster_id": cluster_id,
                "size": len(cluster_articles),
                "avg_sentiment": round(avg_sentiment, 3),
                "top_keywords": top_keywords,
                "example_titles": cluster_articles['title'].head(3).tolist() if 'title' in cluster_articles.columns else [],
                "time_range": {
                    "start": cluster_articles['timestamp'].min(),
                    "end": cluster_articles['timestamp'].max()
                } if 'timestamp' in cluster_articles.columns else {}
            })
        
        return clusters
    
    def _create_youtube_cluster_summaries(self, df: pd.DataFrame, cluster_labels: np.ndarray,
                                        vectorizer: TfidfVectorizer) -> List[Dict]:
        """Create human-readable summaries for YouTube clusters"""
        clusters = []
        
        for cluster_id in range(max(cluster_labels) + 1):
            cluster_mask = cluster_labels == cluster_id
            cluster_videos = df[cluster_mask]
            
            if len(cluster_videos) == 0:
                continue
            
            # Get top keywords from titles
            cluster_titles = cluster_videos['title'].fillna('')
            tfidf_matrix = vectorizer.transform(cluster_titles)
            feature_names = vectorizer.get_feature_names_out()
            
            tfidf_sums = np.array(tfidf_matrix.sum(axis=0)).flatten()
            top_keyword_indices = tfidf_sums.argsort()[-5:][::-1]
            top_keywords = [feature_names[i] for i in top_keyword_indices if tfidf_sums[i] > 0]
            
            # Engagement statistics
            avg_views = cluster_videos['view_count'].mean() if 'view_count' in cluster_videos.columns else 0
            avg_engagement = cluster_videos['engagement_score'].mean() if 'engagement_score' in cluster_videos.columns else 0
            
            clusters.append({
                "cluster_id": cluster_id,
                "size": len(cluster_videos),
                "avg_views": round(avg_views, 0),
                "avg_engagement": round(avg_engagement, 3),
                "top_keywords": top_keywords,
                "example_titles": cluster_videos['title'].head(3).tolist(),
                "time_range": {
                    "start": cluster_videos['timestamp'].min(),
                    "end": cluster_videos['timestamp'].max()
                } if 'timestamp' in cluster_videos.columns else {}
            })
        
        return clusters
    
    def _create_price_cluster_summaries(self, feature_df: pd.DataFrame, cluster_labels: np.ndarray,
                                      commodities: List[str]) -> List[Dict]:
        """Create human-readable summaries for price clusters"""
        clusters = []
        
        for cluster_id in range(max(cluster_labels) + 1):
            cluster_mask = cluster_labels == cluster_id
            cluster_commodities = feature_df[cluster_mask]['commodity'].tolist()
            
            if not cluster_commodities:
                continue
            
            # Get cluster statistics
            cluster_features = feature_df[cluster_mask].select_dtypes(include=[np.number])
            
            clusters.append({
                "cluster_id": cluster_id,
                "size": len(cluster_commodities),
                "commodities": cluster_commodities,
                "avg_price": round(cluster_features['mean_price'].mean(), 2) if 'mean_price' in cluster_features.columns else 0,
                "avg_volatility": round(cluster_features['volatility'].mean(), 3) if 'volatility' in cluster_features.columns else 0,
                "avg_trend": round(cluster_features['trend_slope'].mean(), 4) if 'trend_slope' in cluster_features.columns else 0,
                "characteristics": self._describe_price_cluster_characteristics(cluster_features)
            })
        
        return clusters
    
    def _describe_price_cluster_characteristics(self, cluster_features: pd.DataFrame) -> str:
        """Describe price cluster characteristics"""
        if cluster_features.empty:
            return "No data available"
        
        avg_volatility = cluster_features['volatility'].mean() if 'volatility' in cluster_features.columns else 0
        avg_trend = cluster_features['trend_slope'].mean() if 'trend_slope' in cluster_features.columns else 0
        
        if avg_volatility > 0.2 and avg_trend > 0:
            return "High volatility with upward trend"
        elif avg_volatility > 0.2 and avg_trend < 0:
            return "High volatility with downward trend"
        elif avg_volatility <= 0.2 and avg_trend > 0.01:
            return "Stable with upward trend"
        elif avg_volatility <= 0.2 and avg_trend < -0.01:
            return "Stable with downward trend"
        else:
            return "Stable with minimal trend"
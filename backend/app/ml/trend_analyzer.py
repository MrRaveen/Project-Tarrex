import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.config.mongo_config import get_database
from app.ml.trend_scorer import TrendScorer
import logging

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self):
        self.trend_scorer = TrendScorer()
        self.db = get_database()
    
    def analyze_price_trends(self, lookback_days: int = 30) -> Dict:
        """Analyze food price trends"""
        try:
            collection = self.db['processed_food_prices']
            
            # Get recent price data
            start_date = datetime.now() - timedelta(days=lookback_days)
            query = {
                'timestamp': {'$gte': start_date},
                'price': {'$exists': True}
            }
            
            price_data = list(collection.find(query).sort('timestamp', 1))
            
            if not price_data:
                return {"status": "no_data", "trends": {}}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(price_data)
            
            # Group by commodity and analyze trends
            trends = {}
            commodities = df['commodity'].unique() if 'commodity' in df.columns else ['overall']
            
            for commodity in commodities:
                if commodity == 'overall':
                    commodity_data = df
                else:
                    commodity_data = df[df['commodity'] == commodity]
                
                if len(commodity_data) > 5:  # Minimum data points
                    trend_score = self.trend_scorer.calculate_trend_score(
                        commodity_data, 'price', 'timestamp'
                    )
                    trends[commodity] = trend_score
            
            # Calculate overall price trend
            overall_trend = self.trend_scorer.calculate_trend_score(df, 'price', 'timestamp')
            trends['overall'] = overall_trend
            
            return {
                "status": "success",
                "data_points": len(price_data),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat(),
                    "days": lookback_days
                },
                "trends": trends
            }
            
        except Exception as e:
            logger.error(f"Error analyzing price trends: {str(e)}")
            return {"status": "error", "error": str(e), "trends": {}}
    
    def analyze_weather_trends(self, lookback_days: int = 30) -> Dict:
        """Analyze weather trends"""
        try:
            collection = self.db['processed_weather_data']
            
            # Get recent weather data
            start_date = datetime.now() - timedelta(days=lookback_days)
            query = {
                'timestamp': {'$gte': start_date},
                'temperature': {'$exists': True}
            }
            
            weather_data = list(collection.find(query).sort('timestamp', 1))
            
            if not weather_data:
                return {"status": "no_data", "trends": {}}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(weather_data)
            
            # Analyze weather trends using trend scorer
            weather_scores = self.trend_scorer.score_weather_trends(df)
            
            return {
                "status": "success",
                "data_points": len(weather_data),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat(),
                    "days": lookback_days
                },
                "trends": weather_scores
            }
            
        except Exception as e:
            logger.error(f"Error analyzing weather trends: {str(e)}")
            return {"status": "error", "error": str(e), "trends": {}}
    
    def analyze_tax_trends(self, lookback_days: int = 90) -> Dict:
        """Analyze tax revenue trends"""
        try:
            collection = self.db['processed_tax_data']
            
            # Get recent tax data
            start_date = datetime.now() - timedelta(days=lookback_days)
            query = {
                'timestamp': {'$gte': start_date},
                'revenue': {'$exists': True}
            }
            
            tax_data = list(collection.find(query).sort('timestamp', 1))
            
            if not tax_data:
                return {"status": "no_data", "trends": {}}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(tax_data)
            
            # Group by tax type and analyze trends
            trends = {}
            tax_types = df['tax_type'].unique() if 'tax_type' in df.columns else ['overall']
            
            for tax_type in tax_types:
                if tax_type == 'overall':
                    tax_data_subset = df
                else:
                    tax_data_subset = df[df['tax_type'] == tax_type]
                
                if len(tax_data_subset) > 3:  # Minimum data points for tax data
                    trend_score = self.trend_scorer.calculate_trend_score(
                        tax_data_subset, 'revenue', 'timestamp'
                    )
                    trends[tax_type] = trend_score
            
            # Calculate overall tax trend
            overall_trend = self.trend_scorer.calculate_trend_score(df, 'revenue', 'timestamp')
            trends['overall'] = overall_trend
            
            return {
                "status": "success",
                "data_points": len(tax_data),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat(),
                    "days": lookback_days
                },
                "trends": trends
            }
            
        except Exception as e:
            logger.error(f"Error analyzing tax trends: {str(e)}")
            return {"status": "error", "error": str(e), "trends": {}}
    
    def analyze_news_sentiment_trends(self, lookback_days: int = 30) -> Dict:
        """Analyze news sentiment trends"""
        try:
            collection = self.db['processed_news_data']
            
            # Get recent news data
            start_date = datetime.now() - timedelta(days=lookback_days)
            query = {
                'timestamp': {'$gte': start_date},
                'sentiment_score': {'$exists': True}
            }
            
            news_data = list(collection.find(query).sort('timestamp', 1))
            
            if not news_data:
                return {"status": "no_data", "trends": {}}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(news_data)
            
            # Analyze sentiment trends using trend scorer
            sentiment_scores = self.trend_scorer.score_sentiment_trends(df)
            
            # Additional analysis by category if available
            category_trends = {}
            if 'category' in df.columns:
                for category in df['category'].unique():
                    category_data = df[df['category'] == category]
                    if len(category_data) > 5:
                        category_trend = self.trend_scorer.calculate_trend_score(
                            category_data, 'sentiment_score', 'timestamp'
                        )
                        category_trends[category] = category_trend
            
            return {
                "status": "success",
                "data_points": len(news_data),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat(),
                    "days": lookback_days
                },
                "overall_sentiment": sentiment_scores,
                "category_trends": category_trends
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment trends: {str(e)}")
            return {"status": "error", "error": str(e), "trends": {}}
    
    def analyze_youtube_trends(self, lookback_days: int = 30) -> Dict:
        """Analyze YouTube engagement trends"""
        try:
            collection = self.db['processed_youtube_data']
            
            # Get recent YouTube data
            start_date = datetime.now() - timedelta(days=lookback_days)
            query = {
                'timestamp': {'$gte': start_date},
                'engagement_score': {'$exists': True}
            }
            
            youtube_data = list(collection.find(query).sort('timestamp', 1))
            
            if not youtube_data:
                return {"status": "no_data", "trends": {}}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(youtube_data)
            
            # Analyze engagement trends using trend scorer
            engagement_scores = self.trend_scorer.score_sentiment_trends(df)
            
            # Additional analysis by category if available
            category_trends = {}
            if 'category' in df.columns:
                for category in df['category'].unique():
                    category_data = df[df['category'] == category]
                    if len(category_data) > 5:
                        category_trend = self.trend_scorer.calculate_trend_score(
                            category_data, 'engagement_score', 'timestamp'
                        )
                        category_trends[category] = category_trend
            
            return {
                "status": "success",
                "data_points": len(youtube_data),
                "time_period": {
                    "start": start_date.isoformat(),
                    "end": datetime.now().isoformat(),
                    "days": lookback_days
                },
                "overall_engagement": engagement_scores,
                "category_trends": category_trends
            }
            
        except Exception as e:
            logger.error(f"Error analyzing YouTube trends: {str(e)}")
            return {"status": "error", "error": str(e), "trends": {}}
    
    def get_comprehensive_trend_analysis(self) -> Dict:
        """Get comprehensive trend analysis across all data types"""
        results = {}
        
        results['price_trends'] = self.analyze_price_trends()
        results['weather_trends'] = self.analyze_weather_trends()
        results['tax_trends'] = self.analyze_tax_trends()
        results['news_sentiment_trends'] = self.analyze_news_sentiment_trends()
        results['youtube_trends'] = self.analyze_youtube_trends()
        
        # Generate overall trend insights
        overall_insights = self._generate_overall_insights(results)
        
        return {
            "analysis_timestamp": datetime.now().isoformat(),
            "individual_trends": results,
            "overall_insights": overall_insights
        }
    
    def _generate_overall_insights(self, trend_results: Dict) -> Dict:
        """Generate overall insights from trend analysis"""
        insights = []
        risk_level = "low"
        
        # Check for significant economic trends
        price_trends = trend_results.get('price_trends', {})
        if price_trends.get('status') == 'success':
            overall_price = price_trends.get('trends', {}).get('overall', {})
            if overall_price.get('score', 50) > 70:
                insights.append({
                    "type": "high_price_volatility",
                    "severity": "high",
                    "message": "Significant food price volatility detected"
                })
                risk_level = "high"
        
        # Check for weather anomalies
        weather_trends = trend_results.get('weather_trends', {})
        if weather_trends.get('status') == 'success':
            weather_scores = weather_trends.get('trends', {})
            if weather_scores.get('overall_score', 0) > 65:
                insights.append({
                    "type": "weather_instability",
                    "severity": "medium",
                    "message": "Unstable weather patterns detected"
                })
                risk_level = "medium" if risk_level == "low" else risk_level
        
        # Check for negative sentiment
        sentiment_trends = trend_results.get('news_sentiment_trends', {})
        if sentiment_trends.get('status') == 'success':
            sentiment = sentiment_trends.get('overall_sentiment', {})
            if sentiment.get('overall_score', 50) < 30:
                insights.append({
                    "type": "negative_sentiment",
                    "severity": "medium",
                    "message": "Negative sentiment trending in news"
                })
                risk_level = "medium" if risk_level == "low" else risk_level
        
        return {
            "risk_level": risk_level,
            "insights": insights,
            "insight_count": len(insights)
        }
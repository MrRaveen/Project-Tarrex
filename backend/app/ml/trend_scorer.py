import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class TrendScorer:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def calculate_trend_score(self, data: pd.DataFrame, 
                            value_col: str, 
                            timestamp_col: str = 'timestamp',
                            window_size: int = 7,
                            min_data_points: int = 5) -> Dict:
        """
        Calculate trend score for a time series using multiple metrics
        """
        if len(data) < min_data_points:
            return {"score": 0, "trend": "insufficient_data", "confidence": 0}
        
        df = data.sort_values(timestamp_col).copy()
        df['value'] = df[value_col]
        
        # Calculate various trend metrics
        slope = self._calculate_slope(df['value'])
        r_squared = self._calculate_r_squared(df['value'])
        momentum = self._calculate_momentum(df['value'], window_size)
        volatility = self._calculate_volatility(df['value'], window_size)
        trend_strength = self._calculate_trend_strength(df['value'])
        
        # Combine metrics into a composite score
        raw_score = (slope * 0.3 + r_squared * 0.2 + momentum * 0.2 + 
                    (1 - volatility) * 0.15 + trend_strength * 0.15)
        
        # Normalize score to 0-100 range
        normalized_score = max(0, min(100, 50 + raw_score * 50))
        
        # Determine trend direction
        if slope > 0.1:
            trend_direction = "upward"
        elif slope < -0.1:
            trend_direction = "downward"
        else:
            trend_direction = "stable"
        
        # Calculate confidence based on data quality and metrics consistency
        confidence = min(100, max(0, r_squared * 100 + (1 - volatility) * 50))
        
        return {
            "score": round(normalized_score, 2),
            "trend": trend_direction,
            "confidence": round(confidence, 2),
            "metrics": {
                "slope": round(slope, 4),
                "r_squared": round(r_squared, 4),
                "momentum": round(momentum, 4),
                "volatility": round(volatility, 4),
                "trend_strength": round(trend_strength, 4)
            }
        }
    
    def _calculate_slope(self, values: pd.Series) -> float:
        """Calculate linear regression slope"""
        if len(values) < 2:
            return 0
        x = np.arange(len(values))
        slope, _, _, _, _ = stats.linregress(x, values)
        return slope / np.mean(values) if np.mean(values) != 0 else slope
    
    def _calculate_r_squared(self, values: pd.Series) -> float:
        """Calculate R-squared of linear fit"""
        if len(values) < 2:
            return 0
        x = np.arange(len(values))
        slope, intercept, r_value, _, _ = stats.linregress(x, values)
        return r_value ** 2
    
    def _calculate_momentum(self, values: pd.Series, window: int) -> float:
        """Calculate momentum (recent change rate)"""
        if len(values) < window:
            return 0
        recent = values.iloc[-window:]
        if len(recent) < 2:
            return 0
        return (recent.iloc[-1] - recent.iloc[0]) / abs(recent.iloc[0]) if recent.iloc[0] != 0 else 0
    
    def _calculate_volatility(self, values: pd.Series, window: int) -> float:
        """Calculate volatility (normalized standard deviation)"""
        if len(values) < 2:
            return 1
        rolling_std = values.rolling(window=min(window, len(values))).std().dropna()
        if len(rolling_std) == 0:
            return 1
        mean_abs = abs(values.mean())
        if mean_abs == 0:
            return 1
        return rolling_std.iloc[-1] / mean_abs
    
    def _calculate_trend_strength(self, values: pd.Series) -> float:
        """Calculate trend strength using ADX-like approach"""
        if len(values) < 3:
            return 0
        
        # Simple trend strength calculation
        changes = values.diff().dropna()
        if len(changes) < 2:
            return 0
        
        positive_changes = changes[changes > 0].sum()
        negative_changes = abs(changes[changes < 0].sum())
        
        if positive_changes + negative_changes == 0:
            return 0
        
        return abs(positive_changes - negative_changes) / (positive_changes + negative_changes)
    
    def score_weather_trends(self, weather_data: pd.DataFrame) -> Dict:
        """Score weather trends for Sri Lankan context"""
        if weather_data.empty:
            return {"overall_score": 0, "trends": {}}
        
        trends = {}
        
        # Temperature trend
        if 'temperature' in weather_data.columns:
            temp_score = self.calculate_trend_score(weather_data, 'temperature')
            trends['temperature'] = temp_score
        
        # Rainfall trend
        if 'rainfall' in weather_data.columns:
            rainfall_score = self.calculate_trend_score(weather_data, 'rainfall')
            trends['rainfall'] = rainfall_score
        
        # Humidity trend
        if 'humidity' in weather_data.columns:
            humidity_score = self.calculate_trend_score(weather_data, 'humidity')
            trends['humidity'] = humidity_score
        
        # Calculate overall weather score
        overall_score = self._calculate_overall_weather_score(trends)
        
        return {
            "overall_score": round(overall_score, 2),
            "trends": trends
        }
    
    def _calculate_overall_weather_score(self, trends: Dict) -> float:
        """Calculate overall weather impact score for Sri Lanka"""
        if not trends:
            return 0
        
        weights = {
            'temperature': 0.4,    # High impact on agriculture and energy
            'rainfall': 0.4,       # Critical for water resources and agriculture
            'humidity': 0.2         # Affects comfort and health
        }
        
        total_score = 0
        total_weight = 0
        
        for metric, trend_data in trends.items():
            if metric in weights:
                # For weather, we care about significant changes (positive or negative)
                score = abs(trend_data['score'] - 50) * 2  # Convert to 0-100 scale for deviation
                total_score += score * weights[metric]
                total_weight += weights[metric]
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def score_economic_trends(self, economic_data: pd.DataFrame) -> Dict:
        """Score economic trends for Sri Lankan context"""
        if economic_data.empty:
            return {"overall_score": 0, "trends": {}}
        
        trends = {}
        
        # Food price trends
        if 'price' in economic_data.columns:
            price_score = self.calculate_trend_score(economic_data, 'price')
            trends['food_prices'] = price_score
        
        # Tax revenue trends
        if 'revenue' in economic_data.columns:
            revenue_score = self.calculate_trend_score(economic_data, 'revenue')
            trends['tax_revenue'] = revenue_score
        
        # Calculate overall economic score
        overall_score = self._calculate_overall_economic_score(trends)
        
        return {
            "overall_score": round(overall_score, 2),
            "trends": trends
        }
    
    def _calculate_overall_economic_score(self, trends: Dict) -> float:
        """Calculate overall economic impact score for Sri Lanka"""
        if not trends:
            return 0
        
        weights = {
            'food_prices': 0.6,    # High impact on inflation and cost of living
            'tax_revenue': 0.4     # Important for government stability
        }
        
        total_score = 0
        total_weight = 0
        
        for metric, trend_data in trends.items():
            if metric in weights:
                # For economic metrics, upward trends in prices are negative, revenue positive
                if metric == 'food_prices':
                    # Higher prices are negative for consumers
                    score = max(0, 100 - trend_data['score'])
                else:
                    # Higher revenue is positive
                    score = trend_data['score']
                total_score += score * weights[metric]
                total_weight += weights[metric]
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def score_sentiment_trends(self, sentiment_data: pd.DataFrame) -> Dict:
        """Score sentiment trends from news and social media"""
        if sentiment_data.empty:
            return {"overall_score": 50, "trends": {}}  # Neutral if no data
        
        trends = {}
        
        # News sentiment trend
        if 'sentiment_score' in sentiment_data.columns:
            sentiment_score = self.calculate_trend_score(sentiment_data, 'sentiment_score')
            trends['news_sentiment'] = sentiment_score
        
        # YouTube engagement trend
        if 'engagement_score' in sentiment_data.columns:
            engagement_score = self.calculate_trend_score(sentiment_data, 'engagement_score')
            trends['social_engagement'] = engagement_score
        
        # Calculate overall sentiment score
        overall_score = self._calculate_overall_sentiment_score(trends)
        
        return {
            "overall_score": round(overall_score, 2),
            "trends": trends
        }
    
    def _calculate_overall_sentiment_score(self, trends: Dict) -> float:
        """Calculate overall sentiment score"""
        if not trends:
            return 50  # Neutral
        
        weights = {
            'news_sentiment': 0.6,
            'social_engagement': 0.4
        }
        
        total_score = 0
        total_weight = 0
        
        for metric, trend_data in trends.items():
            if metric in weights:
                total_score += trend_data['score'] * weights[metric]
                total_weight += weights[metric]
        
        return total_score / total_weight if total_weight > 0 else 50
    
    def generate_trend_insights(self, all_scores: Dict) -> List[Dict]:
        """Generate human-readable insights from trend scores"""
        insights = []
        
        # Weather insights
        weather_scores = all_scores.get('weather', {})
        if weather_scores and weather_scores.get('overall_score', 0) > 60:
            insights.append({
                "type": "weather_alert",
                "severity": "high" if weather_scores['overall_score'] > 75 else "medium",
                "message": f"Significant weather pattern detected with score {weather_scores['overall_score']}"
            })
        
        # Economic insights
        economic_scores = all_scores.get('economic', {})
        if economic_scores:
            if economic_scores.get('overall_score', 0) > 70:
                insights.append({
                    "type": "economic_concern",
                    "severity": "high",
                    "message": "High economic volatility detected that may impact stability"
                })
            elif economic_scores.get('overall_score', 0) < 30:
                insights.append({
                    "type": "economic_stability",
                    "severity": "low",
                    "message": "Economic indicators showing stable patterns"
                })
        
        # Sentiment insights
        sentiment_scores = all_scores.get('sentiment', {})
        if sentiment_scores:
            sentiment_score = sentiment_scores.get('overall_score', 50)
            if sentiment_score > 70:
                insights.append({
                    "type": "positive_sentiment",
                    "severity": "medium",
                    "message": "Strong positive sentiment detected in news and social media"
                })
            elif sentiment_score < 30:
                insights.append({
                    "type": "negative_sentiment",
                    "severity": "high",
                    "message": "Negative sentiment trending across media channels"
                })
        
        # Cross-domain insights
        if (weather_scores and economic_scores and 
            weather_scores.get('overall_score', 0) > 65 and 
            economic_scores.get('overall_score', 0) > 65):
            insights.append({
                "type": "compound_risk",
                "severity": "high",
                "message": "Combined weather and economic volatility detected - potential for cascading effects"
            })
        
        return insights
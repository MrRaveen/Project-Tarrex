import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from app.config.mongo_config import get_database
import logging
from scipy import stats
import json

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Feature engineering for situational awareness data"""
    
    def __init__(self):
        self.db = get_database()
    
    def extract_temporal_features(self, data: pd.DataFrame, timestamp_col: str = 'timestamp') -> pd.DataFrame:
        """Extract temporal features from timestamp data"""
        df = data.copy()
        
        if timestamp_col in df.columns:
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            
            # Basic temporal features
            df['hour'] = df[timestamp_col].dt.hour
            df['day_of_week'] = df[timestamp_col].dt.dayofweek
            df['day_of_month'] = df[timestamp_col].dt.day
            df['month'] = df[timestamp_col].dt.month
            df['quarter'] = df[timestamp_col].dt.quarter
            df['year'] = df[timestamp_col].dt.year
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # Cyclical features
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def create_rolling_features(self, data: pd.DataFrame, value_col: str, 
                               window_sizes: List[int] = [3, 7, 30], 
                               timestamp_col: str = 'timestamp') -> pd.DataFrame:
        """Create rolling window features for time series data"""
        df = data.copy()
        
        if timestamp_col in df.columns:
            df = df.sort_values(timestamp_col)
            
            for window in window_sizes:
                # Rolling statistics
                df[f'{value_col}_rolling_mean_{window}'] = df[value_col].rolling(window=window).mean()
                df[f'{value_col}_rolling_std_{window}'] = df[value_col].rolling(window=window).std()
                df[f'{value_col}_rolling_min_{window}'] = df[value_col].rolling(window=window).min()
                df[f'{value_col}_rolling_max_{window}'] = df[value_col].rolling(window=window).max()
                
                # Percentage changes
                df[f'{value_col}_pct_change_{window}'] = df[value_col].pct_change(periods=window)
                
                # Volatility features
                df[f'{value_col}_volatility_{window}'] = df[value_col].rolling(window=window).std() / df[value_col].rolling(window=window).mean()
        
        return df
    
    def create_lag_features(self, data: pd.DataFrame, value_col: str, 
                          lag_periods: List[int] = [1, 2, 3, 7, 30],
                          timestamp_col: str = 'timestamp') -> pd.DataFrame:
        """Create lag features for time series data"""
        df = data.copy()
        
        if timestamp_col in df.columns:
            df = df.sort_values(timestamp_col)
            
            for lag in lag_periods:
                df[f'{value_col}_lag_{lag}'] = df[value_col].shift(lag)
        
        return df
    
    def engineer_news_features(self, news_data: List[Dict]) -> List[Dict]:
        """Engineer features from news data"""
        enhanced_news = []
        
        for article in news_data:
            features = article.copy()
            
            # Text-based features
            text = features.get('content', '') or features.get('title', '')
            
            # Basic text features
            features['text_length'] = len(text)
            features['word_count'] = len(text.split())
            features['avg_word_length'] = np.mean([len(word) for word in text.split()]) if text.split() else 0
            
            # Sentiment intensity features
            features['exclamation_count'] = text.count('!')
            features['question_count'] = text.count('?')
            features['uppercase_ratio'] = sum(1 for char in text if char.isupper()) / len(text) if text else 0
            
            # Temporal features if available
            if 'published_at' in features:
                try:
                    pub_date = pd.to_datetime(features['published_at'])
                    features['hour_of_day'] = pub_date.hour
                    features['day_of_week'] = pub_date.dayofweek
                    features['is_weekend'] = 1 if pub_date.dayofweek in [5, 6] else 0
                except:
                    pass
            
            enhanced_news.append(features)
        
        return enhanced_news
    
    def engineer_weather_features(self, weather_data: List[Dict]) -> List[Dict]:
        """Engineer features from weather data"""
        enhanced_weather = []
        
        for reading in weather_data:
            features = reading.copy()
            
            # Temperature-based features
            temp = features.get('temperature', 0)
            feels_like = features.get('feels_like', temp)
            temp_min = features.get('temp_min', temp)
            temp_max = features.get('temp_max', temp)
            
            features['temp_variance'] = temp_max - temp_min
            features['temp_feels_difference'] = feels_like - temp
            features['is_extreme_temp'] = 1 if temp > 35 or temp < 15 else 0  # Sri Lanka context
            
            # Humidity and pressure features
            humidity = features.get('humidity', 0)
            pressure = features.get('pressure', 0)
            
            features['humidity_pressure_ratio'] = humidity / pressure if pressure else 0
            features['is_high_humidity'] = 1 if humidity > 80 else 0
            
            # Wind features
            wind_speed = features.get('wind_speed', 0)
            wind_deg = features.get('wind_degree', 0)
            
            features['wind_x'] = wind_speed * np.cos(np.radians(wind_deg))
            features['wind_y'] = wind_speed * np.sin(np.radians(wind_deg))
            
            enhanced_weather.append(features)
        
        return enhanced_weather
    
    def engineer_pricing_features(self, pricing_data: List[Dict]) -> List[Dict]:
        """Engineer features from pricing data"""
        enhanced_pricing = []
        
        # Group by item and location for comparative features
        df = pd.DataFrame(pricing_data)
        
        if not df.empty:
            # Calculate relative prices
            item_avg_prices = df.groupby('item')['price'].mean().to_dict()
            location_avg_prices = df.groupby('location')['price'].mean().to_dict()
            
            for item in pricing_data:
                features = item.copy()
                
                price = features.get('price', 0)
                item_name = features.get('item', '')
                location = features.get('location', '')
                
                # Comparative features
                features['price_vs_item_avg'] = price / item_avg_prices.get(item_name, price) if item_avg_prices.get(item_name) else 1
                features['price_vs_location_avg'] = price / location_avg_prices.get(location, price) if location_avg_prices.get(location) else 1
                features['price_volatility'] = abs(features['price_vs_item_avg'] - 1)
                
                # Temporal features if available
                if 'timestamp' in features:
                    try:
                        ts = pd.to_datetime(features['timestamp'])
                        features['day_of_week'] = ts.dayofweek
                        features['is_market_day'] = 1 if ts.dayofweek in [0, 2, 4] else 0  # Common market days
                    except:
                        pass
                
                enhanced_pricing.append(features)
        
        return enhanced_pricing
    
    def engineer_tax_features(self, tax_data: List[Dict]) -> List[Dict]:
        """Engineer features from tax revenue data"""
        enhanced_tax = []
        
        df = pd.DataFrame(tax_data)
        
        if not df.empty and 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
            
            # Calculate growth rates and trends
            for tax_type in df['tax_type'].unique() if 'tax_type' in df.columns else ['revenue']:
                type_df = df[df['tax_type'] == tax_type] if 'tax_type' in df.columns else df
                
                for idx, row in type_df.iterrows():
                    features = row.to_dict()
                    
                    # Time-based features
                    if 'timestamp' in features:
                        ts = pd.to_datetime(features['timestamp'])
                        features['quarter'] = ts.quarter
                        features['fiscal_year'] = ts.year if ts.month >= 4 else ts.year - 1  # Sri Lanka fiscal year
                        features['is_q4'] = 1 if ts.month in [1, 2, 3] else 0  # Q4 of fiscal year
                    
                    # Revenue trends
                    revenue = features.get('amount', 0) or features.get('revenue', 0)
                    
                    # Calculate YoY growth if possible
                    prev_year_data = type_df[type_df['timestamp'] < (ts - timedelta(days=330))]
                    if not prev_year_data.empty:
                        prev_revenue = prev_year_data.iloc[-1]['amount']
                        features['yoy_growth'] = (revenue - prev_revenue) / prev_revenue if prev_revenue else 0
                    
                    enhanced_tax.append(features)
        
        return enhanced_tax
    
    def create_cross_domain_features(self, data_sources: Dict[str, List[Dict]]) -> List[Dict]:
        """Create features that combine information across different data domains"""
        combined_features = []
        
        # Convert all data to DataFrames with timestamps
        dfs = {}
        for source_name, data in data_sources.items():
            if data:
                df = pd.DataFrame(data)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    dfs[source_name] = df
        
        if not dfs:
            return combined_features
        
        # Create combined timeline
        all_timestamps = pd.concat([df['timestamp'] for df in dfs.values()])
        timeline = pd.date_range(all_timestamps.min(), all_timestamps.max(), freq='H')
        
        for ts in timeline:
            features = {'timestamp': ts, 'cross_domain_features': {}}
            
            # Aggregate features from each data source
            for source_name, df in dfs.items():
                # Get data from this time period
                period_data = df[(df['timestamp'] >= ts - timedelta(hours=6)) & 
                               (df['timestamp'] <= ts)]
                
                if not period_data.empty:
                    features['cross_domain_features'][f'{source_name}_count'] = len(period_data)
                    
                    # Add summary statistics for numerical columns
                    numeric_cols = period_data.select_dtypes(include=[np.number]).columns
                    for col in numeric_cols:
                        features['cross_domain_features'][f'{source_name}_{col}_mean'] = period_data[col].mean()
                        features['cross_domain_features'][f'{source_name}_{col}_std'] = period_data[col].std()
            
            combined_features.append(features)
        
        return combined_features
    
    def perform_temporal_analysis(self, data: pd.DataFrame, value_col: str, 
                                timestamp_col: str = 'timestamp') -> Dict[str, Any]:
        """Perform comprehensive temporal analysis on time series data"""
        df = data.copy()
        
        if timestamp_col not in df.columns or value_col not in df.columns:
            return {}
        
        df = df.sort_values(timestamp_col)
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        
        analysis_results = {}
        
        # Time series decomposition
        analysis_results['basic_stats'] = {
            'mean': df[value_col].mean(),
            'std': df[value_col].std(),
            'min': df[value_col].min(),
            'max': df[value_col].max(),
            'count': len(df)
        }
        
        # Trend analysis
        analysis_results['trend_analysis'] = self._analyze_trends(df, value_col, timestamp_col)
        
        # Seasonality analysis
        analysis_results['seasonality_analysis'] = self._analyze_seasonality(df, value_col, timestamp_col)
        
        # Stationarity tests
        analysis_results['stationarity_tests'] = self._test_stationarity(df, value_col)
        
        # Autocorrelation analysis
        analysis_results['autocorrelation'] = self._analyze_autocorrelation(df, value_col)
        
        return analysis_results
    
    def _analyze_trends(self, df: pd.DataFrame, value_col: str, timestamp_col: str) -> Dict:
        """Analyze trends in time series data"""
        results = {}
        
        # Linear trend
        x = np.arange(len(df))
        y = df[value_col].values
        
        if len(y) > 1:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            results['linear_trend'] = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2,
                'p_value': p_value,
                'trend_direction': 'increasing' if slope > 0 else 'decreasing'
            }
        
        # Moving average trends
        for window in [7, 30]:  # Weekly and monthly trends
            if len(df) >= window:
                ma = df[value_col].rolling(window=window).mean()
                results[f'ma_{window}_trend'] = {
                    'current': ma.iloc[-1] if not ma.isna().all() else None,
                    'trend': 'increasing' if ma.iloc[-1] > ma.iloc[-min(10, len(ma))] else 'decreasing'
                }
        
        return results
    
    def _analyze_seasonality(self, df: pd.DataFrame, value_col: str, timestamp_col: str) -> Dict:
        """Analyze seasonality patterns"""
        results = {}
        
        if len(df) < 30:  # Need sufficient data for seasonality analysis
            return results
        
        # Add temporal components
        df['hour'] = df[timestamp_col].dt.hour
        df['day_of_week'] = df[timestamp_col].dt.dayofweek
        df['month'] = df[timestamp_col].dt.month
        
        # Analyze different seasonal patterns
        for period in ['hour', 'day_of_week', 'month']:
            seasonal_means = df.groupby(period)[value_col].mean()
            seasonal_std = df.groupby(period)[value_col].std()
            
            if len(seasonal_means) > 1:
                results[period] = {
                    'means': seasonal_means.to_dict(),
                    'std_devs': seasonal_std.to_dict(),
                    'seasonality_strength': seasonal_std.mean() / seasonal_means.mean() if seasonal_means.mean() else 0
                }
        
        return results
    
    def _test_stationarity(self, df: pd.DataFrame, value_col: str) -> Dict:
        """Perform stationarity tests"""
        results = {}
        
        if len(df) < 50:  # Need sufficient data for stationarity tests
            return results
        
        # Augmented Dickey-Fuller test
        try:
            from statsmodels.tsa.stattools import adfuller
            adf_result = adfuller(df[value_col].dropna())
            results['adf_test'] = {
                'test_statistic': adf_result[0],
                'p_value': adf_result[1],
                'is_stationary': adf_result[1] < 0.05
            }
        except ImportError:
            pass
        
        return results
    
    def _analyze_autocorrelation(self, df: pd.DataFrame, value_col: str) -> Dict:
        """Analyze autocorrelation patterns"""
        results = {}
        
        if len(df) < 20:  # Need sufficient data for autocorrelation
            return results
        
        try:
            from statsmodels.tsa.stattools import acf, pacf
            
            # Autocorrelation function
            acf_values = acf(df[value_col].dropna(), nlags=min(20, len(df)//2))
            pacf_values = pacf(df[value_col].dropna(), nlags=min(10, len(df)//4))
            
            results['acf'] = {
                'values': acf_values.tolist(),
                'significant_lags': [i for i, val in enumerate(acf_values) if abs(val) > 1.96/np.sqrt(len(df))]
            }
            
            results['pacf'] = {
                'values': pacf_values.tolist(),
                'significant_lags': [i for i, val in enumerate(pacf_values) if abs(val) > 1.96/np.sqrt(len(df))]
            }
            
        except ImportError:
            pass
        
        return results
    
    def save_features_to_mongodb(self, features: List[Dict], collection_name: str):
        """Save engineered features to MongoDB"""
        try:
            collection = self.db[collection_name]
            
            if features:
                # Insert features
                result = collection.insert_many(features)
                logger.info(f"Saved {len(result.inserted_ids)} features to {collection_name}")
                
                # Create indexes for efficient querying
                collection.create_index('timestamp')
                if any('location' in feature for feature in features):
                    collection.create_index('location')
                if any('item' in feature for feature in features):
                    collection.create_index('item')
                    
        except Exception as e:
            logger.error(f"Error saving features to MongoDB: {str(e)}")
            raise
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import numpy as np
from scipy import stats
import math

logger = logging.getLogger(__name__)

class NormalizationEngine:
    def __init__(self):
        # Sri Lankan specific normalization parameters
        self.sri_lankan_regions = [
            'Western', 'Central', 'Southern', 'Northern', 'Eastern',
            'North Western', 'North Central', 'Uva', 'Sabaragamuwa'
        ]
        
        # Economic indicators normalization ranges
        self.economic_ranges = {
            'gdp_growth': {'min': -10.0, 'max': 15.0, 'unit': 'percentage'},
            'inflation': {'min': 0.0, 'max': 50.0, 'unit': 'percentage'},
            'unemployment': {'min': 0.0, 'max': 20.0, 'unit': 'percentage'},
            'interest_rate': {'min': 0.0, 'max': 25.0, 'unit': 'percentage'},
            'exchange_rate': {'min': 100.0, 'max': 400.0, 'unit': 'LKR/USD'}
        }
        
        # Weather normalization parameters
        self.weather_ranges = {
            'temperature': {'min': 15.0, 'max': 40.0, 'unit': 'celsius'},
            'humidity': {'min': 0.0, 'max': 100.0, 'unit': 'percentage'},
            'rainfall': {'min': 0.0, 'max': 500.0, 'unit': 'mm'},
            'wind_speed': {'min': 0.0, 'max': 100.0, 'unit': 'km/h'}
        }
    
    def min_max_normalize(self, value: float, min_val: float, max_val: float) -> float:
        """Min-max normalization to [0, 1] range"""
        if value is None or min_val is None or max_val is None:
            return 0.0
            
        if min_val == max_val:
            return 0.5  # Middle value if range is zero
            
        normalized = (value - min_val) / (max_val - min_val)
        
        # Clip to [0, 1] range
        return max(0.0, min(1.0, normalized))
    
    def z_score_normalize(self, value: float, mean: float, std_dev: float) -> float:
        """Z-score normalization"""
        if value is None or mean is None or std_dev is None or std_dev == 0:
            return 0.0
            
        return (value - mean) / std_dev
    
    def normalize_economic_indicator(self, indicator: str, value: float) -> Dict[str, Any]:
        """Normalize economic indicators"""
        if indicator not in self.economic_ranges:
            return {'normalized': 0.0, 'original': value, 'status': 'unknown_indicator'}
        
        range_info = self.economic_ranges[indicator]
        normalized = self.min_max_normalize(value, range_info['min'], range_info['max'])
        
        return {
            'normalized': round(normalized, 4),
            'original': value,
            'indicator': indicator,
            'unit': range_info['unit'],
            'status': 'normalized'
        }
    
    def normalize_weather_data(self, weather_type: str, value: float) -> Dict[str, Any]:
        """Normalize weather data"""
        if weather_type not in self.weather_ranges:
            return {'normalized': 0.0, 'original': value, 'status': 'unknown_type'}
        
        range_info = self.weather_ranges[weather_type]
        normalized = self.min_max_normalize(value, range_info['min'], range_info['max'])
        
        return {
            'normalized': round(normalized, 4),
            'original': value,
            'type': weather_type,
            'unit': range_info['unit'],
            'status': 'normalized'
        }
    
    def normalize_price_data(self, prices: List[float]) -> Dict[str, Any]:
        """Normalize price data"""
        if not prices:
            return {'normalized_prices': [], 'stats': {}, 'status': 'empty_data'}
        
        # Calculate statistics
        prices_array = np.array(prices)
        mean = np.mean(prices_array)
        std_dev = np.std(prices_array)
        median = np.median(prices_array)
        
        # Normalize using z-score
        normalized_prices = [self.z_score_normalize(price, mean, std_dev) for price in prices]
        
        # Also min-max normalize for [0,1] range
        min_price = min(prices)
        max_price = max(prices)
        min_max_normalized = [self.min_max_normalize(price, min_price, max_price) for price in prices]
        
        return {
            'normalized_prices': [round(x, 4) for x in normalized_prices],
            'min_max_normalized': [round(x, 4) for x in min_max_normalized],
            'stats': {
                'mean': round(mean, 2),
                'std_dev': round(std_dev, 2),
                'median': round(median, 2),
                'min': round(min_price, 2),
                'max': round(max_price, 2),
                'count': len(prices)
            },
            'status': 'normalized'
        }
    
    def normalize_temporal_data(self, timestamps: List[datetime]) -> Dict[str, Any]:
        """Normalize temporal data"""
        if not timestamps:
            return {'normalized_timestamps': [], 'stats': {}, 'status': 'empty_data'}
        
        # Convert to Unix timestamps
        unix_timestamps = [ts.timestamp() for ts in timestamps]
        
        # Normalize to [0, 1] range based on time span
        min_ts = min(unix_timestamps)
        max_ts = max(unix_timestamps)
        
        if min_ts == max_ts:
            normalized = [0.5] * len(unix_timestamps)
        else:
            normalized = [(ts - min_ts) / (max_ts - min_ts) for ts in unix_timestamps]
        
        # Calculate temporal statistics
        time_diffs = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
            time_diffs.append(diff)
        
        avg_interval = np.mean(time_diffs) if time_diffs else 0
        interval_std = np.std(time_diffs) if time_diffs else 0
        
        return {
            'normalized_timestamps': [round(ts, 4) for ts in normalized],
            'stats': {
                'time_span_hours': round((max_ts - min_ts) / 3600, 2),
                'avg_interval_hours': round(avg_interval, 2),
                'interval_std_hours': round(interval_std, 2),
                'start_time': min(timestamps).isoformat(),
                'end_time': max(timestamps).isoformat(),
                'data_points': len(timestamps)
            },
            'status': 'normalized'
        }
    
    def normalize_geographic_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Normalize geographic coordinates for Sri Lanka"""
        # Sri Lanka bounding box
        sri_lanka_bbox = {
            'min_lat': 5.916666,  # Dondra Head
            'max_lat': 9.833333,  # Point Pedro
            'min_lon': 79.516666,  # Colombo
            'max_lon': 81.883333   # Sangaman Kanda
        }
        
        if (latitude is None or longitude is None or
            not (sri_lanka_bbox['min_lat'] <= latitude <= sri_lanka_bbox['max_lat']) or
            not (sri_lanka_bbox['min_lon'] <= longitude <= sri_lanka_bbox['max_lon'])):
            return {
                'normalized_lat': 0.5,
                'normalized_lon': 0.5,
                'original_lat': latitude,
                'original_lon': longitude,
                'status': 'outside_sri_lanka'
            }
        
        # Normalize to [0, 1] range within Sri Lanka
        norm_lat = (latitude - sri_lanka_bbox['min_lat']) / (sri_lanka_bbox['max_lat'] - sri_lanka_bbox['min_lat'])
        norm_lon = (longitude - sri_lanka_bbox['min_lon']) / (sri_lanka_bbox['max_lon'] - sri_lanka_bbox['min_lon'])
        
        return {
            'normalized_lat': round(norm_lat, 4),
            'normalized_lon': round(norm_lon, 4),
            'original_lat': round(latitude, 6),
            'original_lon': round(longitude, 6),
            'status': 'normalized'
        }
    
    def detect_outliers(self, values: List[float], method: str = 'zscore', threshold: float = 3.0) -> Dict[str, Any]:
        """Detect outliers in data"""
        if not values:
            return {'outliers': [], 'indices': [], 'count': 0, 'method': method}
        
        values_array = np.array(values)
        outliers = []
        outlier_indices = []
        
        if method == 'zscore':
            # Z-score method
            z_scores = np.abs(stats.zscore(values_array))
            outlier_indices = np.where(z_scores > threshold)[0]
            
        elif method == 'iqr':
            # IQR method
            Q1 = np.percentile(values_array, 25)
            Q3 = np.percentile(values_array, 75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_indices = np.where((values_array < lower_bound) | (values_array > upper_bound))[0]
        
        else:
            return {'outliers': [], 'indices': [], 'count': 0, 'method': 'unknown'}
        
        outliers = values_array[outlier_indices].tolist()
        
        return {
            'outliers': [round(x, 4) for x in outliers],
            'indices': outlier_indices.tolist(),
            'count': len(outliers),
            'method': method,
            'threshold': threshold
        }
    
    def normalize_text_length(self, text: str, max_length: int = 1000) -> Dict[str, Any]:
        """Normalize text length"""
        if not text:
            return {
                'normalized_length': 0.0,
                'original_length': 0,
                'truncated': False,
                'status': 'empty_text'
            }
        
        text_length = len(text)
        normalized = min(1.0, text_length / max_length)
        
        truncated = text_length > max_length
        processed_text = text[:max_length] if truncated else text
        
        return {
            'normalized_length': round(normalized, 4),
            'original_length': text_length,
            'truncated': truncated,
            'processed_text': processed_text,
            'max_length': max_length,
            'status': 'normalized'
        }
    
    def calculate_composite_index(self, indicators: Dict[str, float], weights: Dict[str, float] = None) -> Dict[str, Any]:
        """Calculate composite index from multiple normalized indicators"""
        if not indicators:
            return {'composite_index': 0.0, 'components': {}, 'status': 'no_indicators'}
        
        # Default equal weights if not provided
        if weights is None:
            weights = {key: 1.0/len(indicators) for key in indicators}
        
        # Validate weights sum to 1
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 0.01:  # Allow small floating point error
            # Normalize weights
            weights = {key: weight/weight_sum for key, weight in weights.items()}
        
        composite = 0.0
        component_scores = {}
        
        for indicator, value in indicators.items():
            if indicator in weights:
                component_score = value * weights[indicator]
                composite += component_score
                component_scores[indicator] = round(component_score, 4)
        
        return {
            'composite_index': round(composite, 4),
            'components': component_scores,
            'weights': weights,
            'normalized_indicators': indicators,
            'status': 'calculated'
        }
    
    def normalize_confidence_score(self, confidence: float) -> float:
        """Normalize confidence scores to [0, 1] range"""
        if confidence is None:
            return 0.0
        
        # Assuming confidence is already in reasonable range, just clip
        return max(0.0, min(1.0, confidence))
    
    def calculate_volatility(self, values: List[float], window: int = 5) -> Dict[str, Any]:
        """Calculate volatility of time series data"""
        if not values or len(values) < 2:
            return {'volatility': 0.0, 'rolling_volatility': [], 'window': window}
        
        # Calculate returns
        returns = []
        for i in range(1, len(values)):
            if values[i-1] != 0:  # Avoid division by zero
                ret = (values[i] - values[i-1]) / values[i-1]
                returns.append(ret)
        
        if not returns:
            return {'volatility': 0.0, 'rolling_volatility': [], 'window': window}
        
        # Overall volatility (standard deviation of returns)
        volatility = np.std(returns)
        
        # Rolling volatility
        rolling_volatility = []
        for i in range(len(returns)):
            start = max(0, i - window + 1)
            window_returns = returns[start:i+1]
            if len(window_returns) >= 2:
                roll_vol = np.std(window_returns)
                rolling_volatility.append(roll_vol)
            else:
                rolling_volatility.append(0.0)
        
        return {
            'volatility': round(volatility, 6),
            'rolling_volatility': [round(x, 6) for x in rolling_volatility],
            'window': window,
            'returns': [round(x, 6) for x in returns]
        }
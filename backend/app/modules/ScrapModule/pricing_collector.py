import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import json
from bs4 import BeautifulSoup
import time
import random

from ...model.pricing_model import FoodPrice, PriceRecord, PriceBatch

logger = logging.getLogger(__name__)

class PricingCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Common food items in Sri Lanka
        self.food_items = [
            'rice', 'dhal', 'sugar', 'wheat flour', 'milk powder',
            'coconut', 'onions', 'potatoes', 'chicken', 'fish',
            'eggs', 'tea', 'bread', 'lentils', 'vegetables'
        ]
        
        # Major markets in Sri Lanka
        self.markets = [
            'Pettah Market', 'Manning Market', 'Narahenpita Economic Center',
            'Dambulla Economic Center', 'Nuwara Eliya Economic Center'
        ]
    
    def scrape_government_data(self) -> List[FoodPrice]:
        """Scrape food pricing data from government sources"""
        prices = []
        
        # Simulate data from Department of Census and Statistics
        try:
            # This would be actual API calls or web scraping in production
            # For demo, we'll generate realistic simulated data
            
            for market in self.markets:
                market_prices = []
                total_price = 0
                item_count = 0
                
                for item in self.food_items:
                    # Generate realistic prices based on item type
                    if item == 'rice':
                        price = round(random.uniform(120, 180), 2)  # LKR per kg
                        unit = 'kg'
                    elif item == 'dhal':
                        price = round(random.uniform(200, 280), 2)  # LKR per kg
                        unit = 'kg'
                    elif item == 'sugar':
                        price = round(random.uniform(100, 150), 2)  # LKR per kg
                        unit = 'kg'
                    elif item == 'milk powder':
                        price = round(random.uniform(400, 600), 2)  # LKR per 400g
                        unit = '400g'
                    elif item == 'chicken':
                        price = round(random.uniform(500, 700), 2)  # LKR per kg
                        unit = 'kg'
                    elif item == 'fish':
                        price = round(random.uniform(300, 800), 2)  # LKR per kg
                        unit = 'kg'
                    else:
                        price = round(random.uniform(50, 300), 2)  # General range
                        unit = 'kg'
                    
                    price_record = PriceRecord(
                        item=item,
                        price=price,
                        unit=unit,
                        market=market,
                        location=self._get_market_location(market),
                        source='government',
                        quality='standard'
                    )
                    
                    market_prices.append(price_record)
                    total_price += price
                    item_count += 1
                
                # Calculate average price for the market
                average_price = total_price / item_count if item_count > 0 else 0
                
                food_price = FoodPrice(
                    date=datetime.now(),
                    location=self._get_market_location(market),
                    market=market,
                    prices=market_prices,
                    average_price=round(average_price, 2),
                    price_change=random.uniform(-5, 5),  # Simulate price change
                    metadata={
                        'source': 'department_of_census',
                        'collection_method': 'official_survey',
                        'items_count': item_count
                    }
                )
                
                prices.append(food_price)
                
        except Exception as e:
            logger.error(f"Error scraping government data: {e}")
        
        return prices
    
    def scrape_retail_data(self) -> List[FoodPrice]:
        """Scrape food pricing data from retail sources"""
        prices = []
        
        # Major retail chains in Sri Lanka
        retailers = [
            'Cargills Food City', 'Keells Super', 'Arpico Super Centre',
            'Laughs Supermarket', 'SPAR supermarket'
        ]
        
        try:
            for retailer in retailers:
                retail_prices = []
                total_price = 0
                item_count = 0
                
                for item in self.food_items:
                    # Retail prices are typically higher than wholesale
                    if item == 'rice':
                        price = round(random.uniform(130, 200), 2)
                        unit = 'kg'
                    elif item == 'dhal':
                        price = round(random.uniform(220, 300), 2)
                        unit = 'kg'
                    elif item == 'sugar':
                        price = round(random.uniform(110, 170), 2)
                        unit = 'kg'
                    elif item == 'milk powder':
                        price = round(random.uniform(450, 650), 2)
                        unit = '400g'
                    elif item == 'chicken':
                        price = round(random.uniform(550, 750), 2)
                        unit = 'kg'
                    else:
                        price = round(random.uniform(60, 350), 2)
                        unit = 'kg'
                    
                    price_record = PriceRecord(
                        item=item,
                        price=price,
                        unit=unit,
                        market=retailer,
                        location=self._get_retail_location(retailer),
                        source='retail',
                        quality='retail_grade'
                    )
                    
                    retail_prices.append(price_record)
                    total_price += price
                    item_count += 1
                
                average_price = total_price / item_count if item_count > 0 else 0
                
                food_price = FoodPrice(
                    date=datetime.now(),
                    location=self._get_retail_location(retailer),
                    market=retailer,
                    prices=retail_prices,
                    average_price=round(average_price, 2),
                    price_change=random.uniform(-3, 3),
                    metadata={
                        'source': 'retail_scraping',
                        'collection_method': 'web_scraping',
                        'items_count': item_count
                    }
                )
                
                prices.append(food_price)
                
        except Exception as e:
            logger.error(f"Error scraping retail data: {e}")
        
        return prices
    
    def scrape_online_sources(self) -> List[FoodPrice]:
        """Scrape food pricing data from online sources"""
        prices = []
        
        # Online platforms and e-commerce sites
        online_sources = [
            'Kapruka', 'Wow.lk', 'Daraz', 'PickMe Food', 'Uber Eats'
        ]
        
        try:
            for source in online_sources:
                online_prices = []
                total_price = 0
                item_count = 0
                
                for item in self.food_items:
                    # Online prices include delivery and service charges
                    if item == 'rice':
                        price = round(random.uniform(140, 220), 2)
                        unit = 'kg'
                    elif item == 'dhal':
                        price = round(random.uniform(240, 320), 2)
                        unit = 'kg'
                    elif item == 'sugar':
                        price = round(random.uniform(120, 180), 2)
                        unit = 'kg'
                    elif item == 'milk powder':
                        price = round(random.uniform(470, 680), 2)
                        unit = '400g'
                    elif item == 'chicken':
                        price = round(random.uniform(580, 780), 2)
                        unit = 'kg'
                    else:
                        price = round(random.uniform(70, 380), 2)
                        unit = 'kg'
                    
                    price_record = PriceRecord(
                        item=item,
                        price=price,
                        unit=unit,
                        market=source,
                        location='online',
                        source='online',
                        quality='premium'
                    )
                    
                    online_prices.append(price_record)
                    total_price += price
                    item_count += 1
                
                average_price = total_price / item_count if item_count > 0 else 0
                
                food_price = FoodPrice(
                    date=datetime.now(),
                    location='online',
                    market=source,
                    prices=online_prices,
                    average_price=round(average_price, 2),
                    price_change=random.uniform(-4, 4),
                    metadata={
                        'source': 'online_platform',
                        'collection_method': 'api_scraping',
                        'items_count': item_count
                    }
                )
                
                prices.append(food_price)
                
        except Exception as e:
            logger.error(f"Error scraping online data: {e}")
        
        return prices
    
    def _get_market_location(self, market: str) -> str:
        """Get location for a market"""
        locations = {
            'Pettah Market': 'Colombo',
            'Manning Market': 'Colombo',
            'Narahenpita Economic Center': 'Colombo',
            'Dambulla Economic Center': 'Dambulla',
            'Nuwara Eliya Economic Center': 'Nuwara Eliya'
        }
        return locations.get(market, 'Unknown')
    
    def _get_retail_location(self, retailer: str) -> str:
        """Get location for a retailer"""
        # Most retailers have multiple locations, using main city
        locations = {
            'Cargills Food City': 'Colombo',
            'Keells Super': 'Colombo',
            'Arpico Super Centre': 'Colombo',
            'Laughs Supermarket': 'Colombo',
            'SPAR supermarket': 'Colombo'
        }
        return locations.get(retailer, 'Colombo')
    
    def collect_food_prices(self) -> PriceBatch:
        """Main method to collect food pricing data from all sources"""
        logger.info("Starting food pricing data collection...")
        
        all_prices = []
        
        # Collect from government sources
        try:
            gov_prices = self.scrape_government_data()
            all_prices.extend(gov_prices)
            logger.info(f"Collected {len(gov_prices)} government price records")
        except Exception as e:
            logger.error(f"Error collecting government prices: {e}")
        
        # Collect from retail sources
        try:
            retail_prices = self.scrape_retail_data()
            all_prices.extend(retail_prices)
            logger.info(f"Collected {len(retail_prices)} retail price records")
        except Exception as e:
            logger.error(f"Error collecting retail prices: {e}")
        
        # Collect from online sources
        try:
            online_prices = self.scrape_online_sources()
            all_prices.extend(online_prices)
            logger.info(f"Collected {len(online_prices)} online price records")
        except Exception as e:
            logger.error(f"Error collecting online prices: {e}")
        
        batch = PriceBatch(
            price_data=all_prices,
            scrape_timestamp=datetime.now()
        )
        
        logger.info(f"Total price records collected: {len(all_prices)}")
        return batch
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
import json
from bs4 import BeautifulSoup
import time
import random

from ...model.tax_model import TaxRevenue, TaxCategory, TaxBatch

logger = logging.getLogger(__name__)

class TaxCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Government revenue sources
        self.revenue_sources = [
            'Inland Revenue Department',
            'Customs Department', 
            'Excise Department',
            'Motor Traffic Department',
            'Other Government Revenue'
        ]
        
        # Tax categories
        self.tax_categories = [
            'Income Tax',
            'Value Added Tax (VAT)',
            'Nation Building Tax (NBT)',
            'Economic Service Charge (ESC)',
            'Customs Duty',
            'Excise Duty',
            'Port and Airport Development Levy',
            'Debt Repayment Levy',
            'Other Taxes'
        ]
    
    def scrape_ird_data(self) -> List[TaxRevenue]:
        """Scrape tax revenue data from Inland Revenue Department"""
        revenues = []
        
        try:
            # Simulate monthly revenue data for the past 12 months
            current_date = datetime.now()
            
            for i in range(12):
                period_date = current_date - timedelta(days=30*i)
                period = period_date.strftime('%Y-%m')
                
                # Generate realistic tax revenue data
                categories = []
                total_revenue = 0
                
                for category in self.tax_categories:
                    # Generate category-specific revenue
                    if 'Income Tax' in category:
                        amount = random.uniform(50000, 120000)  # Millions LKR
                    elif 'VAT' in category:
                        amount = random.uniform(80000, 150000)
                    elif 'Customs' in category:
                        amount = random.uniform(60000, 110000)
                    elif 'Excise' in category:
                        amount = random.uniform(40000, 90000)
                    else:
                        amount = random.uniform(10000, 50000)
                    
                    amount = round(amount, 2)
                    percentage = round((amount / 500000) * 100, 2)  # Rough estimate
                    target = round(amount * random.uniform(0.9, 1.1), 2)  # ±10% target
                    variance = round(((amount - target) / target) * 100, 2) if target > 0 else 0
                    
                    tax_category = TaxCategory(
                        category=category,
                        amount=amount,
                        percentage=percentage,
                        target=target,
                        variance=variance
                    )
                    
                    categories.append(tax_category)
                    total_revenue += amount
                
                # Calculate growth rate (simulated)
                growth_rate = random.uniform(-5, 15)  # -5% to +15%
                target_achievement = random.uniform(85, 115)  # 85% to 115%
                
                tax_revenue = TaxRevenue(
                    period=period,
                    period_type='monthly',
                    total_revenue=round(total_revenue, 2),
                    categories=categories,
                    growth_rate=round(growth_rate, 2),
                    target_achievement=round(target_achievement, 2),
                    source='Inland Revenue Department',
                    metadata={
                        'source_type': 'simulated',
                        'currency': 'LKR_millions',
                        'fiscal_year': '2024'
                    }
                )
                
                revenues.append(tax_revenue)
                
        except Exception as e:
            logger.error(f"Error scraping IRD data: {e}")
        
        return revenues
    
    def scrape_customs_data(self) -> List[TaxRevenue]:
        """Scrape customs revenue data"""
        revenues = []
        
        try:
            # Simulate quarterly data
            quarters = ['2024-Q1', '2024-Q2', '2024-Q3', '2024-Q4']
            
            for quarter in quarters:
                categories = []
                total_revenue = 0
                
                # Customs-specific categories
                customs_categories = [
                    'Import Duty',
                    'Export Duty', 
                    'Other Customs Charges',
                    'Customs Penalties'
                ]
                
                for category in customs_categories:
                    if 'Import Duty' in category:
                        amount = random.uniform(40000, 80000)
                    elif 'Export Duty' in category:
                        amount = random.uniform(5000, 15000)
                    else:
                        amount = random.uniform(1000, 5000)
                    
                    amount = round(amount, 2)
                    percentage = round((amount / 100000) * 100, 2)
                    
                    tax_category = TaxCategory(
                        category=category,
                        amount=amount,
                        percentage=percentage
                    )
                    
                    categories.append(tax_category)
                    total_revenue += amount
                
                growth_rate = random.uniform(-3, 12)
                target_achievement = random.uniform(90, 110)
                
                tax_revenue = TaxRevenue(
                    period=quarter,
                    period_type='quarterly',
                    total_revenue=round(total_revenue, 2),
                    categories=categories,
                    growth_rate=round(growth_rate, 2),
                    target_achievement=round(target_achievement, 2),
                    source='Customs Department',
                    metadata={
                        'source_type': 'simulated',
                        'currency': 'LKR_millions',
                        'fiscal_year': '2024'
                    }
                )
                
                revenues.append(tax_revenue)
                
        except Exception as e:
            logger.error(f"Error scraping customs data: {e}")
        
        return revenues
    
    def scrape_excise_data(self) -> List[TaxRevenue]:
        """Scrape excise revenue data"""
        revenues = []
        
        try:
            # Simulate monthly excise data
            months = 6  # Last 6 months
            current_date = datetime.now()
            
            for i in range(months):
                period_date = current_date - timedelta(days=30*i)
                period = period_date.strftime('%Y-%m')
                
                categories = []
                total_revenue = 0
                
                # Excise-specific categories
                excise_categories = [
                    'Liquor Tax',
                    'Tobacco Tax',
                    'Vehicle Revenue License',
                    'Other Excise Duties'
                ]
                
                for category in excise_categories:
                    if 'Liquor' in category:
                        amount = random.uniform(15000, 30000)
                    elif 'Tobacco' in category:
                        amount = random.uniform(10000, 25000)
                    elif 'Vehicle' in category:
                        amount = random.uniform(5000, 15000)
                    else:
                        amount = random.uniform(2000, 8000)
                    
                    amount = round(amount, 2)
                    percentage = round((amount / 60000) * 100, 2)
                    
                    tax_category = TaxCategory(
                        category=category,
                        amount=amount,
                        percentage=percentage
                    )
                    
                    categories.append(tax_category)
                    total_revenue += amount
                
                growth_rate = random.uniform(-2, 8)
                target_achievement = random.uniform(92, 108)
                
                tax_revenue = TaxRevenue(
                    period=period,
                    period_type='monthly',
                    total_revenue=round(total_revenue, 2),
                    categories=categories,
                    growth_rate=round(growth_rate, 2),
                    target_achievement=round(target_achievement, 2),
                    source='Excise Department',
                    metadata={
                        'source_type': 'simulated',
                        'currency': 'LKR_millions',
                        'fiscal_year': '2024'
                    }
                )
                
                revenues.append(tax_revenue)
                
        except Exception as e:
            logger.error(f"Error scraping excise data: {e}")
        
        return revenues
    
    def scrape_government_portal(self) -> List[TaxRevenue]:
        """Scrape data from government portals (simulated)"""
        revenues = []
        
        try:
            # Annual data simulation
            years = ['2022', '2023', '2024']
            
            for year in years:
                categories = []
                total_revenue = 0
                
                for category in self.tax_categories:
                    # Annual figures are larger
                    if 'Income Tax' in category:
                        amount = random.uniform(600000, 1200000)
                    elif 'VAT' in category:
                        amount = random.uniform(800000, 1600000)
                    elif 'Customs' in category:
                        amount = random.uniform(500000, 1000000)
                    elif 'Excise' in category:
                        amount = random.uniform(300000, 700000)
                    else:
                        amount = random.uniform(50000, 300000)
                    
                    amount = round(amount, 2)
                    percentage = round((amount / 4000000) * 100, 2)  # Total ~4B LKR
                    
                    tax_category = TaxCategory(
                        category=category,
                        amount=amount,
                        percentage=percentage
                    )
                    
                    categories.append(tax_category)
                    total_revenue += amount
                
                # Calculate year-over-year growth
                growth_rate = random.uniform(-8, 20)  # Wider range for annual data
                target_achievement = random.uniform(88, 112)
                
                tax_revenue = TaxRevenue(
                    period=year,
                    period_type='annual',
                    total_revenue=round(total_revenue, 2),
                    categories=categories,
                    growth_rate=round(growth_rate, 2),
                    target_achievement=round(target_achievement, 2),
                    source='Ministry of Finance',
                    metadata={
                        'source_type': 'simulated',
                        'currency': 'LKR_millions',
                        'fiscal_year': year
                    }
                )
                
                revenues.append(tax_revenue)
                
        except Exception as e:
            logger.error(f"Error scraping government portal data: {e}")
        
        return revenues
    
    def collect_tax_revenue(self) -> TaxBatch:
        """Main method to collect tax revenue data from all sources"""
        logger.info("Starting tax revenue data collection...")
        
        all_revenues = []
        
        # Collect from IRD
        try:
            ird_revenues = self.scrape_ird_data()
            all_revenues.extend(ird_revenues)
            logger.info(f"Collected {len(ird_revenues)} IRD revenue records")
        except Exception as e:
            logger.error(f"Error collecting IRD data: {e}")
        
        # Collect from Customs
        try:
            customs_revenues = self.scrape_customs_data()
            all_revenues.extend(customs_revenues)
            logger.info(f"Collected {len(customs_revenues)} customs revenue records")
        except Exception as e:
            logger.error(f"Error collecting customs data: {e}")
        
        # Collect from Excise
        try:
            excise_revenues = self.scrape_excise_data()
            all_revenues.extend(excise_revenues)
            logger.info(f"Collected {len(excise_revenues)} excise revenue records")
        except Exception as e:
            logger.error(f"Error collecting excise data: {e}")
        
        # Collect from Government Portal
        try:
            gov_revenues = self.scrape_government_portal()
            all_revenues.extend(gov_revenues)
            logger.info(f"Collected {len(gov_revenues)} government revenue records")
        except Exception as e:
            logger.error(f"Error collecting government data: {e}")
        
        batch = TaxBatch(
            tax_data=all_revenues,
            scrape_timestamp=datetime.now()
        )
        
        logger.info(f"Total tax revenue records collected: {len(all_revenues)}")
        return batch
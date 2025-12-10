import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import html
from bs4 import BeautifulSoup
import unicodedata

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        # Common Sri Lankan location patterns
        self.sri_lankan_locations = [
            'colombo', 'kandy', 'galle', 'jaffna', 'trincomalee', 'anuradhapura',
            'badulla', 'matara', 'ratnapura', 'kurunegala', 'gampaha', 'kalutara',
            'batticaloa', 'puttalam', 'nuwara eliya', 'polonnaruwa', 'kegalle',
            'monaragala', 'hambantota', 'vavuniya', 'mullaitivu', 'kilinochchi'
        ]
        
        # Common Sri Lankan currency patterns
        self.currency_patterns = [
            r'Rs\.?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'LKR\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # USD
        ]
        
        # Common noise patterns
        self.noise_patterns = [
            r'\[.*?\]',  # Square brackets
            r'\(.*?\)',  # Parentheses
            r'\b(?:click|read|more|here|source|via)\b',
            r'\b(?:http|https|www\.)\S+',  # URLs
            r'\b\d{1,2}:\d{2}\s*(?:AM|PM)\b',  # Time patterns
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text or not isinstance(text, str):
            return ""
        
        try:
            # Decode HTML entities
            text = html.unescape(text)
            
            # Remove HTML tags
            text = self._remove_html_tags(text)
            
            # Normalize unicode
            text = unicodedata.normalize('NFKC', text)
            
            # Remove noise patterns
            for pattern in self.noise_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Remove leading/trailing punctuation
            text = text.strip('.,!?;:-\'"()[]{}')
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text if isinstance(text, str) else ""
    
    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text"""
        try:
            soup = BeautifulSoup(text, 'html.parser')
            return soup.get_text()
        except:
            # Fallback regex method
            return re.sub(r'<[^>]+>', '', text)
    
    def extract_currency_values(self, text: str) -> List[float]:
        """Extract currency values from text"""
        values = []
        
        for pattern in self.currency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Remove commas and convert to float
                    value_str = match.replace(',', '')
                    value = float(value_str)
                    values.append(value)
                except (ValueError, TypeError):
                    continue
        
        return values
    
    def normalize_location(self, location: str) -> str:
        """Normalize location names"""
        if not location or not isinstance(location, str):
            return "unknown"
        
        location = location.lower().strip()
        
        # Check if it's a known Sri Lankan location
        for known_loc in self.sri_lankan_locations:
            if known_loc in location:
                return known_loc.title()
        
        # Common location variations
        location_mappings = {
            'colombo': ['colombo', 'cmb', 'colombo city'],
            'kandy': ['kandy', 'kdy', 'mahanuwara'],
            'galle': ['galle', 'gll', 'galle fort'],
            'jaffna': ['jaffna', 'jfn', 'yarlpanam'],
            'trincomalee': ['trincomalee', 'trinco', 'tco'],
        }
        
        for normalized, variations in location_mappings.items():
            if any(var in location for var in variations):
                return normalized.title()
        
        return location.title()
    
    def clean_numeric_value(self, value: Any) -> Optional[float]:
        """Clean and convert numeric values"""
        if value is None:
            return None
            
        if isinstance(value, (int, float)):
            return float(value)
            
        if isinstance(value, str):
            try:
                # Remove commas, spaces, and currency symbols
                cleaned = re.sub(r'[^\d.]', '', value)
                if cleaned:
                    return float(cleaned)
            except (ValueError, TypeError):
                pass
        
        return None
    
    def clean_date(self, date_str: Any) -> Optional[datetime]:
        """Clean and parse date strings"""
        if date_str is None:
            return None
            
        if isinstance(date_str, datetime):
            return date_str
            
        if not isinstance(date_str, str):
            return None
        
        # Common date formats in Sri Lankan context
        date_formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%Y.%m.%d',
            '%b %d, %Y',
            '%d %b %Y',
            '%B %d, %Y',
            '%d %B %Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y %H:%M',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try to extract date from messy strings
        try:
            # Look for common patterns
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}/\d{2}/\d{4})',
                r'(\d{2}-\d{2}-\d{4})',
                r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
                r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, date_str, re.IGNORECASE)
                if match:
                    extracted = match.group(1)
                    for fmt in date_formats:
                        try:
                            return datetime.strptime(extracted, fmt)
                        except ValueError:
                            continue
        except:
            pass
        
        return None
    
    def remove_duplicates(self, items: List[Dict[str, Any]], key_fields: List[str]) -> List[Dict[str, Any]]:
        """Remove duplicate items based on key fields"""
        if not items or not key_fields:
            return items
        
        seen = set()
        unique_items = []
        
        for item in items:
            # Create a unique key based on specified fields
            key_parts = []
            for field in key_fields:
                value = item.get(field)
                if value is not None:
                    if isinstance(value, str):
                        value = self.clean_text(value.lower())
                    key_parts.append(str(value))
            
            key = '|'.join(key_parts)
            
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        return unique_items
    
    def validate_data_completeness(self, data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Validate data completeness and return validation results"""
        validation = {
            'is_complete': True,
            'missing_fields': [],
            'invalid_fields': [],
            'completeness_score': 0.0
        }
        
        total_fields = len(required_fields)
        valid_count = 0
        
        for field in required_fields:
            value = data.get(field)
            
            if value is None or value == "" or (isinstance(value, (list, dict)) and not value):
                validation['missing_fields'].append(field)
                validation['is_complete'] = False
            else:
                valid_count += 1
        
        validation['completeness_score'] = round((valid_count / total_fields) * 100, 2) if total_fields > 0 else 100.0
        
        return validation
    
    def clean_phone_numbers(self, phone: str) -> Optional[str]:
        """Clean and format Sri Lankan phone numbers"""
        if not phone or not isinstance(phone, str):
            return None
        
        # Remove all non-digit characters
        cleaned = re.sub(r'\D', '', phone)
        
        # Sri Lankan phone number patterns
        if cleaned.startswith('94'):
            # International format: +94xxxxxxxxx
            if len(cleaned) == 11:  # +947xxxxxxxx
                return f"+{cleaned}"
            elif len(cleaned) == 12:  # +9411xxxxxxx
                return f"+{cleaned}"
        elif cleaned.startswith('0'):
            # Local format: 0xxxxxxxxx
            if len(cleaned) == 10:  # 07xxxxxxxx
                return f"+94{cleaned[1:]}"
            elif len(cleaned) == 11:  # 011xxxxxxx
                return f"+94{cleaned[1:]}"
        
        return None
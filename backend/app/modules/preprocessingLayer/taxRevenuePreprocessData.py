# tasks.py
# from celery import current_task
from io import BytesIO, StringIO
from celery import Celery
import pandas as pd
import numpy as np
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def parse_xml_observation(obs_element) -> Dict[str, Any]:
    """Parse a single XML observation element into a dictionary."""
    data = {}
    
    # Parse ObsKey values
    obs_key = obs_element.find('.//{*}ObsKey')
    if obs_key is not None:
        for value_elem in obs_key.findall('.//{*}Value'):
            key = value_elem.get('id')
            val = value_elem.get('value')
            if key and val:
                data[key] = val
    
    # Parse ObsValue
    obs_value = obs_element.find('.//{*}ObsValue')
    if obs_value is not None:
        try:
            data['OBS_VALUE'] = float(obs_value.get('value', 0))
        except (ValueError, TypeError):
            data['OBS_VALUE'] = 0.0
    
    # Parse Attributes
    attributes = obs_element.find('.//{*}Attributes')
    if attributes is not None:
        for value_elem in attributes.findall('.//{*}Value'):
            key = value_elem.get('id')
            val = value_elem.get('value')
            if key and val:
                data[key] = val
    return data

def preprocess_tax_revenue_data(xml_content: str) -> pd.DataFrame:
    """
    Preprocess XML tax revenue data.
    
    Args:
        xml_content: XML string containing the data
        
    Returns:
        Preprocessed pandas DataFrame
    """
    try:
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Extract namespace
        namespace = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
        ns = {'generic': namespace} if namespace else {}
        
        # Find all observation elements
        obs_elements = root.findall('.//{*}Obs', ns) or root.findall('.//Obs')
        
        # Parse each observation
        records = []
        for obs_element in obs_elements:
            record = parse_xml_observation(obs_element)
            if record:
                records.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        if df.empty:
            return df
        
        # 1. Convert OBS_VALUE with unit multiplier
        if 'OBS_VALUE' in df.columns and 'UNIT_MULT' in df.columns:
            # Convert UNIT_MULT to numeric multiplier (e.g., '6' means 10^6 = 1,000,000)
            df['UNIT_MULT'] = pd.to_numeric(df['UNIT_MULT'], errors='coerce').fillna(0)
            df['OBS_VALUE_ADJUSTED'] = df['OBS_VALUE'] * (10 ** df['UNIT_MULT'])
        
        # 2. Convert data types
        if 'TIME_PERIOD' in df.columns:
            # Ensure year is integer
            df['TIME_PERIOD'] = pd.to_numeric(df['TIME_PERIOD'], errors='coerce')
            df['TIME_PERIOD'] = df['TIME_PERIOD'].astype('Int64')
        
        if 'DECIMALS' in df.columns:
            df['DECIMALS'] = pd.to_numeric(df['DECIMALS'], errors='coerce').fillna(0).astype(int)
        
        # 3. Handle categorical columns
        categorical_cols = ['REF_AREA', 'MEASURE', 'SECTOR', 'STANDARD_REVENUE', 
                          'CTRY_SPECIFIC_REVENUE', 'UNIT_MEASURE', 'FREQ', 'OBS_STATUS']
        
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        # 4. Create derived features
        if 'TIME_PERIOD' in df.columns:
            # Create decade feature
            df['DECADE'] = (df['TIME_PERIOD'] // 10) * 10
            
            # Create year-over-year identifier
            df['YEAR_TYPE'] = df['TIME_PERIOD'].apply(
                lambda x: 'LEAP' if (x % 4 == 0 and x % 100 != 0) or (x % 400 == 0) else 'COMMON'
            )
        
        # 5. Handle missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in ['OBS_VALUE', 'OBS_VALUE_ADJUSTED']:
                # For revenue values, fill with 0 or forward fill
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna(df[col].median())
        
        # 6. Create revenue category based on values
        if 'OBS_VALUE_ADJUSTED' in df.columns:
            bins = [0, 1000, 10000, 100000, 1000000, float('inf')]
            labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
            df['REVENUE_CATEGORY'] = pd.cut(df['OBS_VALUE_ADJUSTED'], bins=bins, labels=labels)
        
        # 7. Add metadata columns
        df['PROCESSING_TIMESTAMP'] = datetime.now()
        df['DATA_SOURCE'] = 'OECD_TAX_REVENUE'
        df['ROW_HASH'] = pd.util.hash_pandas_object(df, index=False).astype(str)
        
        # 8. Sort and reset index
        sort_cols = []
        if 'TIME_PERIOD' in df.columns:
            sort_cols.append('TIME_PERIOD')
        if 'REF_AREA' in df.columns:
            sort_cols.append('REF_AREA')
        
        if sort_cols:
            df = df.sort_values(by=sort_cols).reset_index(drop=True)
        
        logger.info(f"Preprocessed {len(df)} rows successfully")
        return df
        
    except Exception as e:
        logger.error(f"Error preprocessing XML data: {str(e)}")
        raise

try:
    # Try to get Celery from your main app
    from ...config.celery_app import celery_app
except ImportError:
    # Create a standalone Celery instance if needed
    celery_app = Celery('preprocess_tasks')

# Celery task
@celery_app.task(bind=True, name='preprocess_tax_revenue') 
def preprocess_tax_revenue_task(self, xml_data: str, task_id: str = None) -> Dict[str, Any]:
    """
    Celery task to fetch and preprocess tax revenue data.
    
    Args:
        uri: Data source URI
        task_id: Optional task ID for tracking
        
    Returns:
        Dictionary containing preprocessing results
    """
    try:
        # Fetch XML data
        xml_content = xml_data
        if xml_content is None:
            return {
                'success': False,
                'error': 'Failed to fetch data from source',
                'task_id': task_id
            }
        
        # Preprocess data
        df = preprocess_tax_revenue_data(xml_content)
        
        # Convert DataFrame to serializable format
        result = {
            'success': True,
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'dataframe_info': {
                'num_rows': len(df),
                'num_columns': len(df.columns),
                'columns': df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            },
            'sample_data': df.head(10).to_dict('records') if not df.empty else [],
            'summary_stats': {
                'total_revenue': float(df['OBS_VALUE_ADJUSTED'].sum()) if 'OBS_VALUE_ADJUSTED' in df.columns else 0,
                'avg_revenue': float(df['OBS_VALUE_ADJUSTED'].mean()) if 'OBS_VALUE_ADJUSTED' in df.columns else 0,
                'years_covered': df['TIME_PERIOD'].unique().tolist() if 'TIME_PERIOD' in df.columns else []
            }
        }
        
        logger.info(f"Task completed successfully: {len(df)} rows processed")
        return result
        
    except Exception as e:
        logger.error(f"Task failed with error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'task_id': task_id,
            'timestamp': datetime.now().isoformat()
        }
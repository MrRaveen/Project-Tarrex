import requests
import pandas as pd
from io import StringIO
import logging
import uuid
import time
from celery.result import AsyncResult

logger = logging.getLogger(__name__)

class scrapTaxRevenueDataAll:
    def scrapTaxRevenueData(self):
        try:
            uri = "https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_REV_ASAP@DF_REVLKA,2.0/LKA..S13....A?startPeriod=2014&dimensionAtObservation=AllDimensions"
            
            # Debug: Check if Celery is properly imported
            logger.info("=" * 60)
            logger.info("STARTING DATA SCRAPING AND PREPROCESSING")
            logger.info("=" * 60)
            
            # 1. Fetch data
            logger.info(f"📡 Fetching data from: {uri}")
            response = requests.get(uri, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch data. Status: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
            logger.info(f"✅ Data fetched: {len(response.text)} characters")
            
            # 2. Try to parse as CSV for debugging
            try:
                df = pd.read_csv(StringIO(response.text))
                logger.info(f"📊 CSV Parsed successfully!")
                logger.info(f"   Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                logger.info(f"   First 3 columns: {df.columns.tolist()[:3]}")
                
                if not df.empty:
                    # Show first row for debugging
                    first_row = df.iloc[0]
                    logger.info(f"   First row sample:")
                    for col in df.columns.tolist()[:5]:  # First 5 columns
                        if col in first_row:
                            logger.info(f"     {col}: {first_row[col]}")
            except Exception as e:
                logger.error(f"❌ CSV Parsing failed: {str(e)}")
                logger.info(f"   First 200 chars of response: {response.text[:200]}")
                logger.info(f"   Content-Type header: {response.headers.get('Content-Type')}")
            
            # 3. Submit to Celery
            task_id = str(uuid.uuid4())
            logger.info(f"🔄 Submitting to Celery...")
            logger.info(f"   Task ID: {task_id}")
            
            # Import Celery app to check
            try:
                from ...config.celery_app import celery_app
                logger.info(f"✅ Celery app imported successfully")
            except ImportError as e:
                logger.error(f"❌ Failed to import Celery app: {str(e)}")
                return {"success": False, "error": f"Celery import failed: {str(e)}"}
            
            # Submit the task
            try:
                from ..preprocessingLayer.taxRevenuePreprocessData import preprocess_tax_revenue_task
                task = preprocess_tax_revenue_task.delay(response.text, task_id)
                logger.info(f"✅ Task submitted to Celery")
                logger.info(f"   Celery Task ID: {task.id}")
            except Exception as e:
                logger.error(f"❌ Failed to submit task: {str(e)}")
                return {"success": False, "error": f"Task submission failed: {str(e)}"}
            
            # 4. Wait for task completion with better debugging
            logger.info(f"⏳ Waiting for task completion (checking every 2 seconds)...")
            
            for i in range(15):  # Wait up to 30 seconds (15 * 2)
                time.sleep(2)
                
                # Check task status
                task_result = AsyncResult(task.id, app=celery_app)
                
                logger.info(f"   Check {i+1}/15 - Task state: {task_result.state}")
                
                if task_result.ready():
                    result = task_result.result
                    
                    if result.get('success'):
                        logger.info(f"✅ Task completed successfully!")
                        
                        # Log preprocessing results
                        df_info = result.get('dataframe_info', {})
                        logger.info(f"📈 Preprocessed DataFrame: {df_info.get('num_rows', 0)} rows")
                        logger.info(f"   Columns: {', '.join(df_info.get('columns', [])[:5])}...")
                        
                        # Log sample data
                        sample = result.get('sample_data', [])
                        if sample:
                            logger.info(f"   Sample row 1: {sample[0]}")
                        
                        return {
                            "success": True,
                            "task_id": task_id,
                            "celery_task_id": task.id,
                            "result": result
                        }
                    else:
                        logger.error(f"❌ Task failed: {result.get('error')}")
                        return {
                            "success": False,
                            "error": result.get('error'),
                            "task_id": task_id,
                            "celery_task_id": task.id
                        }
            
            logger.error(f"⏰ Task timed out after 30 seconds")
            logger.info(f"   Last known state: {task_result.state}")
            
            return {
                "success": False,
                "error": "Task execution timed out",
                "task_id": task_id,
                "celery_task_id": task.id,
                "state": task_result.state
            }
            
        except Exception as e:
            logger.error(f"💥 Unexpected error in scrapTaxRevenueData: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}



# from io import StringIO
# from multiprocessing.pool import AsyncResult
# from time import time
# from flask import jsonify
# # from flask_caching import logger
# import requests
# import pandas as pd
# import logging
# from ...config.celery_app import celery_app

# logger = logging.getLogger(__name__)
# from ..preprocessingLayer.taxRevenuePreprocessData import preprocess_tax_revenue_task

# class scrapTaxRevenueDataAll:
#     def scrapTaxRevenueData(self):
#         try:
#             uri = "https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_REV_ASAP@DF_REVLKA,2.0/LKA..S13....A?startPeriod=2014&dimensionAtObservation=AllDimensions"
#             response = requests.get(uri)
#             df = pd.read_csv(StringIO(response.text))
#             logger.error(f"Scraped DataFrame: ")
#             preprocessedData = preprocess_tax_revenue_task.delay(response.text)
#             # logger.error(f"Preprocessing task : {preprocessedData}")
#             #testing area
#             logger.info(f"Submitted Celery task ID: {preprocessedData.id}")
            
#             # Wait for task completion (for testing only - synchronous)
#             logger.info("Waiting for task completion...")
#             for i in range(20):  # Wait up to 10 seconds
#                 time.sleep(1)
#                 task_result = AsyncResult(preprocessedData.id, app=celery_app)
                
#                 if task_result.ready():
#                     result = task_result.result
#                     logger.info(f"Task completed after {i+1} seconds")
                    
#                     if result.get('success'):
#                         # Log preprocessed data info
#                         df_info = result.get('dataframe_info', {})
#                         logger.info(f"✓ Preprocessing successful!")
#                         logger.info(f"  Rows processed: {df_info.get('num_rows', 0)}")
#                         logger.info(f"  Columns: {df_info.get('num_columns', 0)}")
#                         logger.info(f"  Column names: {df_info.get('columns', [])}")
                        
#                         # Log sample data
#                         sample_data = result.get('sample_data', [])
#                         if sample_data:
#                             logger.info(f"  Sample data (first {len(sample_data)} rows):")
#                             for idx, row in enumerate(sample_data, 1):
#                                 logger.info(f"    Row {idx}: {row}")
                        
#                         # Log summary stats
#                         summary = result.get('summary_stats', {})
#                         if summary:
#                             logger.info(f"  Total revenue: {summary.get('total_revenue', 0)}")
#                             logger.info(f"  Average revenue: {summary.get('avg_revenue', 0)}")
#                             logger.info(f"  Years covered: {summary.get('years_covered', [])}")
#                     else:
#                         logger.error(f"✗ Preprocessing failed: {result.get('error', 'Unknown error')}")
#         except Exception as e:
#             return {"success": False, "error": str(e)}   



# import requests
# import xml.etree.ElementTree as ET
# import pandas as pd
# from flask import jsonify
# from datetime import datetime

# def scrapTaxRevenueData():
#     try:
#         uri = "https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_REV_ASAP@DF_REVLKA,2.0/LKA..S13....A?startPeriod=2014&dimensionAtObservation=AllDimensions"
        
#         # Make request
#         response = requests.get(uri, timeout=30)
#         response.raise_for_status()
        
#         # Parse XML (it's XML, not CSV!)
#         root = ET.fromstring(response.content)
        
#         # Define SDMX namespaces
#         namespaces = {
#             'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
#             'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message'
#         }
        
#         # Extract data
#         data_points = []
        
#         # Find all series elements
#         for series in root.findall('.//generic:Series', namespaces):
#             # Get series key (dimensions)
#             series_key = {}
#             for key_value in series.findall('generic:SeriesKey/generic:Value', namespaces):
#                 concept = key_value.get('concept')
#                 value = key_value.get('value')
#                 if concept and value:
#                     series_key[concept] = value
            
#             # Get observations
#             for obs in series.findall('generic:Obs', namespaces):
#                 record = series_key.copy()
                
#                 # Get time period
#                 time_elem = obs.find('generic:ObsDimension', namespaces)
#                 if time_elem is not None:
#                     record['TIME_PERIOD'] = time_elem.get('value')
                
#                 # Get value
#                 value_elem = obs.find('generic:ObsValue', namespaces)
#                 if value_elem is not None:
#                     record['OBS_VALUE'] = value_elem.get('value')
                
#                 # Get attributes if any
#                 for attr in obs.findall('generic:Attributes/generic:Value', namespaces):
#                     concept = attr.get('concept')
#                     value = attr.get('value')
#                     if concept and value:
#                         record[concept] = value
                
#                 data_points.append(record)
        
#         # Convert to DataFrame
#         if data_points:
#             df = pd.DataFrame(data_points)
#             # Convert OBS_VALUE to numeric if possible
#             if 'OBS_VALUE' in df.columns:
#                 df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
            
#             return {
#                 'success': True,
#                 'data': df.to_dict(orient='records'),
#                 'count': len(df),
#                 'columns': df.columns.tolist(),
#                 'sample': df.head().to_dict(orient='records')
#             }
#         else:
#             return {
#                 'success': False,
#                 'error': 'No data found in the response',
#                 'raw_response': response.text[:500]  # First 500 chars for debugging
#             }
            
#     except Exception as e:
#         return {
#             'success': False, 
#             'error': str(e),
#             'type': type(e).__name__
#         }

# from io import StringIO
# import requests
# import pandas as pd
# import xml.etree.ElementTree as ET
# from datetime import datetime

# def scrapTaxRevenueData():
#     try:
#         uri = "https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_REV_ASAP@DF_REVLKA,2.0/LKA..S13....A?startPeriod=2014&dimensionAtObservation=AllDimensions"
        
#         # Make request
#         response = requests.get(uri, timeout=30)
#         response.raise_for_status()
        
#         # Check if response is XML (SDMX usually returns XML)
#         content_type = response.headers.get('Content-Type', '').lower()
        
#         if 'xml' in content_type or response.text.strip().startswith('<?xml'):
#             # Parse XML
#             root = ET.fromstring(response.content)
            
#             # Define SDMX namespaces
#             namespaces = {
#                 'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
#                 'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message'
#             }
            
#             # Extract data
#             data_points = []
            
#             # Find all series elements
#             series_elements = root.findall('.//generic:Series', namespaces)
            
#             if not series_elements:
#                 # Try without namespace
#                 series_elements = root.findall('.//Series')
#                 namespaces = {}  # Reset namespaces
            
#             for series in series_elements:
#                 # Get series key (dimensions)
#                 series_key = {}
#                 key_values = series.findall('generic:SeriesKey/generic:Value', namespaces) if namespaces else series.findall('SeriesKey/Value')
                
#                 for key_value in key_values:
#                     concept = key_value.get('concept')
#                     value = key_value.get('value')
#                     if concept and value:
#                         series_key[concept] = value
                
#                 # Get observations
#                 observations = series.findall('generic:Obs', namespaces) if namespaces else series.findall('Obs')
                
#                 for obs in observations:
#                     record = series_key.copy()
                    
#                     # Get time period
#                     time_elem = obs.find('generic:ObsDimension', namespaces) if namespaces else obs.find('ObsDimension')
#                     if time_elem is not None:
#                         record['TIME_PERIOD'] = time_elem.get('value')
                    
#                     # Get value
#                     value_elem = obs.find('generic:ObsValue', namespaces) if namespaces else obs.find('ObsValue')
#                     if value_elem is not None:
#                         record['OBS_VALUE'] = value_elem.get('value')
                    
#                     data_points.append(record)
            
#             # Convert to DataFrame
#             if data_points:
#                 df = pd.DataFrame(data_points)
#                 # Return the DataFrame directly
#                 return df
#             else:
#                 # Return empty DataFrame with error message
#                 return pd.DataFrame({'error': ['No data found in XML response']})
        
#         else:
#             # Try as CSV
#             df = pd.read_csv(StringIO(response.text))
#             return df
            
#     except pd.errors.ParserError:
#         # Not CSV, try other formats or return error
#         return pd.DataFrame({'error': ['Could not parse response as CSV']})
#     except Exception as e:
#         # Return DataFrame with error, not dict
#         return pd.DataFrame({'error': [str(e)]})    
    
    
     
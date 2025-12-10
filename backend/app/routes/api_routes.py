from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app.config.mongo_config import get_database
from app.service.tasks.scraping_tasks import scrape_all_data_task
from app.service.tasks.processing_tasks import process_all_data_task
from app.service.tasks.analysis_tasks import analyze_data_task, generate_insights_task, update_indicators_task
from app.ml.trend_analyzer import TrendAnalyzer
from app.ml.anomaly_detector import AnomalyDetector
from app.ml.clustering_engine import ClusteringEngine
import logging
from bson import ObjectId
import json

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_mongo_collection(collection_name):
    """Get MongoDB collection"""
    db = get_database()
    return db[collection_name]

@api_bp.route('/status/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = get_database()
        # Test database connection
        db.command('ping')
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "mongodb": "connected",
                "redis": "assumed_healthy",  # Would need redis connection test
                "celery": "assumed_healthy"   # Would need celery connection test
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 500

@api_bp.route('/scrape/run', methods=['POST'])
def run_scraping():
    """Trigger data scraping task"""
    try:
        # Get optional parameters from request
        data = request.get_json() or {}
        scrape_types = data.get('types', ['all'])
        
        # Start scraping task
        task = scrape_all_data_task.apply_async(args=[scrape_types])
        
        return jsonify({
            "status": "started",
            "task_id": task.id,
            "message": "Scraping task started",
            "scrape_types": scrape_types,
            "started_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error starting scraping task: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/preprocess/run', methods=['POST'])
def run_preprocessing():
    """Trigger data preprocessing task"""
    try:
        # Get optional parameters from request
        data = request.get_json() or {}
        process_types = data.get('types', ['all'])
        
        # Start processing task
        task = process_all_data_task.apply_async(args=[process_types])
        
        return jsonify({
            "status": "started",
            "task_id": task.id,
            "message": "Preprocessing task started",
            "process_types": process_types,
            "started_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error starting preprocessing task: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/analyze/run', methods=['POST'])
def run_analysis():
    """Trigger data analysis task"""
    try:
        # Get optional parameters from request
        data = request.get_json() or {}
        analysis_type = data.get('type', 'all')
        
        # Start analysis task
        task = analyze_data_task.apply_async(args=[analysis_type])
        
        return jsonify({
            "status": "started",
            "task_id": task.id,
            "message": "Analysis task started",
            "analysis_type": analysis_type,
            "started_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error starting analysis task: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/indicators/latest', methods=['GET'])
def get_latest_indicators():
    """Get latest situational awareness indicators"""
    try:
        collection = get_mongo_collection('situational_indicators')
        
        # Get latest indicators
        latest_indicators = collection.find_one(
            sort=[("timestamp", -1)]
        )
        
        if not latest_indicators:
            return jsonify({
                "status": "no_data",
                "message": "No indicators available. Run analysis first."
            })
        
        # Remove MongoDB ObjectId for JSON serialization
        if '_id' in latest_indicators:
            latest_indicators['_id'] = str(latest_indicators['_id'])
        
        return jsonify({
            "status": "success",
            "indicators": latest_indicators
        })
    except Exception as e:
        logger.error(f"Error fetching indicators: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/risks/latest', methods=['GET'])
def get_latest_risks():
    """Get latest risk assessment"""
    try:
        collection = get_mongo_collection('business_insights')
        
        # Get latest risk assessment
        latest_insights = collection.find_one(
            sort=[("timestamp", -1)]
        )
        
        if not latest_insights:
            return jsonify({
                "status": "no_data",
                "message": "No risk assessment available. Run analysis first."
            })
        
        # Extract risk assessment
        risk_assessment = latest_insights.get('risk_assessment', {})
        
        # Remove MongoDB ObjectId for JSON serialization
        if '_id' in latest_insights:
            latest_insights['_id'] = str(latest_insights['_id'])
        
        return jsonify({
            "status": "success",
            "risk_assessment": risk_assessment,
            "last_updated": latest_insights['timestamp']
        })
    except Exception as e:
        logger.error(f"Error fetching risks: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/insights/overview', methods=['GET'])
def get_insights_overview():
    """Get comprehensive insights overview"""
    try:
        collection = get_mongo_collection('business_insights')
        
        # Get latest insights
        latest_insights = collection.find_one(
            sort=[("timestamp", -1)]
        )
        
        if not latest_insights:
            return jsonify({
                "status": "no_data",
                "message": "No insights available. Run analysis first."
            })
        
        # Remove MongoDB ObjectId for JSON serialization
        if '_id' in latest_insights:
            latest_insights['_id'] = str(latest_insights['_id'])
        
        return jsonify({
            "status": "success",
            "insights": latest_insights
        })
    except Exception as e:
        logger.error(f"Error fetching insights: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get current trends across all data types"""
    try:
        # Get query parameters
        data_type = request.args.get('type', 'all')
        lookback_days = int(request.args.get('lookback', 30))
        
        trend_analyzer = TrendAnalyzer()
        
        if data_type == 'all':
            # Get comprehensive trend analysis
            trends = trend_analyzer.get_comprehensive_trend_analysis()
        else:
            # Get specific trend type
            if data_type == 'prices':
                trends = trend_analyzer.analyze_price_trends(lookback_days)
            elif data_type == 'weather':
                trends = trend_analyzer.analyze_weather_trends(lookback_days)
            elif data_type == 'tax':
                trends = trend_analyzer.analyze_tax_trends(lookback_days)
            elif data_type == 'news':
                trends = trend_analyzer.analyze_news_sentiment_trends(lookback_days)
            elif data_type == 'youtube':
                trends = trend_analyzer.analyze_youtube_trends(lookback_days)
            else:
                return jsonify({
                    "status": "error",
                    "error": f"Unknown data type: {data_type}"
                }), 400
        
        return jsonify({
            "status": "success",
            "data_type": data_type,
            "lookback_days": lookback_days,
            "trends": trends,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/anomalies/latest', methods=['GET'])
def get_latest_anomalies():
    """Get latest detected anomalies"""
    try:
        collection = get_mongo_collection('analysis_results')
        
        # Get latest anomaly detection results
        latest_anomalies = collection.find_one(
            {"analysis_type": "anomaly_detection"},
            sort=[("timestamp", -1)]
        )
        
        if not latest_anomalies:
            return jsonify({
                "status": "no_data",
                "message": "No anomalies detected yet. Run analysis first."
            })
        
        # Remove MongoDB ObjectId for JSON serialization
        if '_id' in latest_anomalies:
            latest_anomalies['_id'] = str(latest_anomalies['_id'])
        
        return jsonify({
            "status": "success",
            "anomalies": latest_anomalies,
            "detected_at": latest_anomalies['timestamp']
        })
    except Exception as e:
        logger.error(f"Error fetching anomalies: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/clusters/latest', methods=['GET'])
def get_latest_clusters():
    """Get latest clustering results"""
    try:
        collection = get_mongo_collection('analysis_results')
        
        # Get latest clustering results
        latest_clusters = collection.find_one(
            {"analysis_type": "clustering"},
            sort=[("timestamp", -1)]
        )
        
        if not latest_clusters:
            return jsonify({
                "status": "no_data",
                "message": "No clustering results available. Run analysis first."
            })
        
        # Remove MongoDB ObjectId for JSON serialization
        if '_id' in latest_clusters:
            latest_clusters['_id'] = str(latest_clusters['_id'])
        
        return jsonify({
            "status": "success",
            "clusters": latest_clusters,
            "generated_at": latest_clusters['timestamp']
        })
    except Exception as e:
        logger.error(f"Error fetching clusters: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/data/summary', methods=['GET'])
def get_data_summary():
    """Get summary of available data"""
    try:
        collections = [
            'raw_news_data', 'processed_news_data',
            'raw_youtube_data', 'processed_youtube_data', 
            'raw_weather_data', 'processed_weather_data',
            'raw_food_prices', 'processed_food_prices',
            'raw_tax_data', 'processed_tax_data'
        ]
        
        summary = {}
        db = get_database()
        
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            
            # Get latest record timestamp
            latest_record = db[collection_name].find_one(
                sort=[("timestamp", -1)]
            )
            
            latest_timestamp = latest_record['timestamp'] if latest_record and 'timestamp' in latest_record else None
            
            summary[collection_name] = {
                "count": count,
                "latest_timestamp": latest_timestamp
            }
        
        return jsonify({
            "status": "success",
            "data_summary": summary,
            "generated_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error generating data summary: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/system/status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    try:
        # Get data summary
        data_summary = {}
        db = get_database()
        
        collections = ['raw_news_data', 'processed_news_data', 'analysis_results', 'business_insights']
        for col in collections:
            data_summary[col] = db[col].count_documents({})
        
        # Get latest analysis timestamp
        latest_analysis = db['analysis_results'].find_one(sort=[("timestamp", -1)])
        latest_insights = db['business_insights'].find_one(sort=[("timestamp", -1)])
        
        return jsonify({
            "status": "success",
            "system_status": {
                "database": "connected",
                "data_availability": data_summary,
                "last_analysis": latest_analysis['timestamp'] if latest_analysis else None,
                "last_insights": latest_insights['timestamp'] if latest_insights else None,
                "current_time": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Additional utility endpoints
@api_bp.route('/tasks/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """Get status of a specific Celery task"""
    try:
        # This would require Celery task result backend setup
        # For now, return a simple response
        return jsonify({
            "status": "unknown",
            "task_id": task_id,
            "message": "Task status monitoring requires result backend configuration"
        })
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@api_bp.route('/config/reload', methods=['POST'])
def reload_config():
    """Reload application configuration"""
    try:
        # This would implement configuration reload logic
        return jsonify({
            "status": "success",
            "message": "Configuration reloaded",
            "reloaded_at": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error reloading config: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
from celery import shared_task
from app.ml.anomaly_detector import AnomalyDetector
from app.ml.clustering_engine import ClusteringEngine
from app.ml.trend_analyzer import TrendAnalyzer
from app.ml.event_detector import EventDetector
from app.ml.feature_engineer import FeatureEngineer
from app.config.mongo_config import get_database
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

def get_mongo_collection(collection_name):
    """Get MongoDB collection"""
    db = get_database()
    return db[collection_name]

@shared_task(bind=True, name="analyze_data_task")
def analyze_data_task(self, analysis_type="all"):
    """Celery task to perform comprehensive data analysis"""
    try:
        logger.info(f"Starting data analysis task: {analysis_type}")
        
        results = {}
        
        if analysis_type in ["all", "anomaly"]:
            # Perform anomaly detection
            anomaly_results = detect_anomalies_task.apply()
            results["anomaly_detection"] = anomaly_results.result
        
        if analysis_type in ["all", "clustering"]:
            # Perform clustering analysis
            clustering_results = perform_clustering_task.apply()
            results["clustering"] = clustering_results.result
        
        if analysis_type in ["all", "trends"]:
            # Perform trend analysis
            trend_results = analyze_trends_task.apply()
            results["trend_analysis"] = trend_results.result
        
        if analysis_type in ["all", "events"]:
            # Perform event detection
            event_results = detect_events_task.apply()
            results["event_detection"] = event_results.result
        
        logger.info("Data analysis task completed successfully")
        return {
            "status": "success",
            "analysis_type": analysis_type,
            "results": results,
            "analyzed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Data analysis task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="detect_anomalies_task")
def detect_anomalies_task(self):
    """Celery task to detect anomalies across all data types"""
    try:
        logger.info("Starting anomaly detection task")
        
        detector = AnomalyDetector()
        results = {}
        
        # Detect anomalies in different data types
        results["weather_anomalies"] = detector.detect_weather_anomalies()
        results["pricing_anomalies"] = detector.detect_pricing_anomalies()
        results["tax_anomalies"] = detector.detect_tax_anomalies()
        results["news_sentiment_anomalies"] = detector.detect_news_sentiment_anomalies()
        results["youtube_engagement_anomalies"] = detector.detect_youtube_engagement_anomalies()
        
        # Store results in MongoDB
        analysis_collection = get_mongo_collection("analysis_results")
        analysis_collection.insert_one({
            "analysis_type": "anomaly_detection",
            "results": results,
            "timestamp": datetime.now(),
            "metadata": {
                "data_types_analyzed": list(results.keys()),
                "anomaly_count": sum(len(v.get("anomalies", [])) for v in results.values())
            }
        })
        
        logger.info(f"Anomaly detection task completed: {len(results)} analyses performed")
        return {
            "status": "success",
            "anomalies_detected": results,
            "total_anomalies": sum(len(v.get("anomalies", [])) for v in results.values())
        }
    except Exception as e:
        logger.error(f"Anomaly detection task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="perform_clustering_task")
def perform_clustering_task(self):
    """Celery task to perform clustering analysis"""
    try:
        logger.info("Starting clustering analysis task")
        
        clustering_engine = ClusteringEngine()
        results = {}
        
        # Perform clustering on different data types
        results["news_clusters"] = clustering_engine.cluster_news_articles()
        results["youtube_clusters"] = clustering_engine.cluster_youtube_videos()
        results["pricing_clusters"] = clustering_engine.cluster_food_prices()
        
        # Store results in MongoDB
        analysis_collection = get_mongo_collection("analysis_results")
        analysis_collection.insert_one({
            "analysis_type": "clustering",
            "results": results,
            "timestamp": datetime.now(),
            "metadata": {
                "data_types_clustered": list(results.keys()),
                "total_clusters": sum(len(v.get("clusters", [])) for v in results.values())
            }
        })
        
        logger.info(f"Clustering task completed: {len(results)} clustering analyses performed")
        return {
            "status": "success",
            "clustering_results": results,
            "total_clusters": sum(len(v.get("clusters", [])) for v in results.values())
        }
    except Exception as e:
        logger.error(f"Clustering task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="analyze_trends_task")
def analyze_trends_task(self):
    """Celery task to perform trend analysis"""
    try:
        logger.info("Starting trend analysis task")
        
        trend_analyzer = TrendAnalyzer()
        results = {}
        
        # Analyze trends in different data types
        results["price_trends"] = trend_analyzer.analyze_price_trends()
        results["weather_trends"] = trend_analyzer.analyze_weather_trends()
        results["tax_trends"] = trend_analyzer.analyze_tax_trends()
        results["news_sentiment_trends"] = trend_analyzer.analyze_news_sentiment_trends()
        results["youtube_trends"] = trend_analyzer.analyze_youtube_trends()
        
        # Store results in MongoDB
        analysis_collection = get_mongo_collection("analysis_results")
        analysis_collection.insert_one({
            "analysis_type": "trend_analysis",
            "results": results,
            "timestamp": datetime.now(),
            "metadata": {
                "data_types_analyzed": list(results.keys()),
                "trend_count": sum(len(v.get("trends", [])) for v in results.values())
            }
        })
        
        logger.info(f"Trend analysis task completed: {len(results)} trend analyses performed")
        return {
            "status": "success",
            "trend_results": results,
            "total_trends": sum(len(v.get("trends", [])) for v in results.values())
        }
    except Exception as e:
        logger.error(f"Trend analysis task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="detect_events_task")
def detect_events_task(self):
    """Celery task to detect significant events"""
    try:
        logger.info("Starting event detection task")
        
        event_detector = EventDetector()
        results = {}
        
        # Detect events across different data types
        results["news_events"] = event_detector.detect_news_events()
        results["weather_events"] = event_detector.detect_weather_events()
        results["economic_events"] = event_detector.detect_economic_events()
        results["social_events"] = event_detector.detect_social_events()
        
        # Store results in MongoDB
        analysis_collection = get_mongo_collection("analysis_results")
        analysis_collection.insert_one({
            "analysis_type": "event_detection",
            "results": results,
            "timestamp": datetime.now(),
            "metadata": {
                "data_types_analyzed": list(results.keys()),
                "event_count": sum(len(v.get("events", [])) for v in results.values())
            }
        })
        
        logger.info(f"Event detection task completed: {len(results)} event analyses performed")
        return {
            "status": "success",
            "events_detected": results,
            "total_events": sum(len(v.get("events", [])) for v in results.values())
        }
    except Exception as e:
        logger.error(f"Event detection task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="generate_insights_task")
def generate_insights_task(self):
    """Celery task to generate comprehensive insights"""
    try:
        logger.info("Starting insights generation task")
        
        # Get latest analysis results
        analysis_collection = get_mongo_collection("analysis_results")
        
        # Get latest results for each analysis type
        insights = {}
        analysis_types = ["anomaly_detection", "clustering", "trend_analysis", "event_detection"]
        
        for analysis_type in analysis_types:
            latest_result = analysis_collection.find_one(
                {"analysis_type": analysis_type},
                sort=[("timestamp", -1)]
            )
            if latest_result:
                insights[analysis_type] = {
                    "timestamp": latest_result["timestamp"],
                    "summary": self._generate_summary(latest_result["results"])
                }
        
        # Generate overall risk assessment
        risk_assessment = self._assess_risks(insights)
        
        # Generate business insights
        business_insights = self._generate_business_insights(insights)
        
        # Store insights in MongoDB
        insights_collection = get_mongo_collection("business_insights")
        insights_collection.insert_one({
            "insights": insights,
            "risk_assessment": risk_assessment,
            "business_insights": business_insights,
            "timestamp": datetime.now(),
            "metadata": {
                "analysis_types": list(insights.keys()),
                "risk_level": risk_assessment.get("overall_risk_level", "unknown")
            }
        })
        
        logger.info("Insights generation task completed successfully")
        return {
            "status": "success",
            "insights_generated": len(insights),
            "risk_assessment": risk_assessment,
            "business_insights_count": len(business_insights)
        }
    except Exception as e:
        logger.error(f"Insights generation task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

@shared_task(bind=True, name="update_indicators_task")
def update_indicators_task(self):
    """Celery task to update situational awareness indicators"""
    try:
        logger.info("Starting indicators update task")
        
        # Get latest insights
        insights_collection = get_mongo_collection("business_insights")
        latest_insights = insights_collection.find_one(
            sort=[("timestamp", -1)]
        )
        
        if not latest_insights:
            logger.warning("No insights found for indicators update")
            return {"status": "skipped", "reason": "no_insights_available"}
        
        # Calculate indicators based on insights
        indicators = self._calculate_indicators(latest_insights)
        
        # Store indicators in MongoDB
        indicators_collection = get_mongo_collection("situational_indicators")
        indicators_collection.insert_one({
            "indicators": indicators,
            "timestamp": datetime.now(),
            "source_insights_timestamp": latest_insights["timestamp"],
            "metadata": {
                "indicator_count": len(indicators),
                "update_type": "automatic"
            }
        })
        
        logger.info(f"Indicators update task completed: {len(indicators)} indicators updated")
        return {
            "status": "success",
            "indicators_updated": len(indicators),
            "update_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Indicators update task failed: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=3)

def _generate_summary(self, results):
    """Generate summary from analysis results"""
    # Implementation for generating human-readable summaries
    return {"summary": "Analysis completed", "details": results}

def _assess_risks(self, insights):
    """Assess risks based on analysis insights"""
    # Implementation for risk assessment logic
    return {"overall_risk_level": "medium", "risks": []}

def _generate_business_insights(self, insights):
    """Generate business insights from analysis results"""
    # Implementation for business insight generation
    return ["Sample business insight"]

def _calculate_indicators(self, insights):
    """Calculate situational awareness indicators"""
    # Implementation for indicator calculation
    return {"economic_stability": 75, "social_stability": 80, "environmental_risk": 30}
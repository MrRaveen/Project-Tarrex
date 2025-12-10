from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import logging
import uuid
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Backend API configuration
BACKEND_URL = "http://localhost:5000"  # Backend API URL

class BackendAPI:
    """Client for interacting with the backend API."""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.api_key = "your_api_key_here"  # Change this in production
    
    def _get_headers(self):
        """Get request headers with API key."""
        return {"X-API-Key": self.api_key}
    
    def get_health(self):
        """Check backend health."""
        try:
            response = requests.get(f"{self.base_url}/status/health", 
                                 timeout=10, 
                                 headers=self._get_headers())
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_queue_status(self, detailed=False):
        """Get Celery queue status."""
        try:
            params = {"detailed": detailed}
            response = requests.get(f"{self.base_url}/status/queues", 
                                 params=params, 
                                 timeout=10,
                                 headers=self._get_headers())
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Queue status check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_indicators(self):
        """Get latest indicators."""
        try:
            response = requests.get(f"{self.base_url}/indicators/latest", 
                                 timeout=30,
                                 headers=self._get_headers())
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get indicators: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_risks(self):
        """Get latest risks."""
        try:
            response = requests.get(f"{self.base_url}/risks/latest", 
                                 timeout=30,
                                 headers=self._get_headers())
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get risks: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_insights(self):
        """Get insights overview."""
        try:
            response = requests.get(f"{self.base_url}/insights/overview", 
                                 timeout=30,
                                 headers=self._get_headers())
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get insights: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_trends(self, data_type="all", lookback_days=30):
        """Get trends data."""
        try:
            params = {"type": data_type, "lookback": lookback_days}
            response = requests.get(
                f"{self.base_url}/trends", 
                params=params, 
                timeout=30,
                headers=self._get_headers()
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get trends: {e}")
            return {"status": "error", "error": str(e)}
    
    def trigger_scraping(self, sources=None):
        """Trigger scraping pipeline."""
        try:
            payload = {"sources": sources or ["news", "weather", "prices", "tax", "youtube"]}
            response = requests.post(
                f"{self.base_url}/scrape/run", 
                json=payload, 
                timeout=60,
                headers=self._get_headers()
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to trigger scraping: {e}")
            return {"status": "error", "error": str(e)}
    
    def trigger_processing(self):
        """Trigger processing pipeline."""
        try:
            response = requests.post(f"{self.base_url}/preprocess/run", 
                                  timeout=60,
                                  headers=self._get_headers())
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to trigger processing: {e}")
            return {"status": "error", "error": str(e)}
    
    def trigger_analysis(self):
        """Trigger analysis pipeline."""
        try:
            response = requests.post(f"{self.base_url}/analyze/run", 
                                  timeout=60,
                                  headers=self._get_headers())
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to trigger analysis: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_system_status(self):
        """Get comprehensive system status."""
        try:
            response = requests.get(f"{self.base_url}/system/status", 
                                 timeout=30,
                                 headers=self._get_headers())
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get system status: {e}")
            return {"status": "error", "error": str(e)}

# Initialize backend API client
backend_api = BackendAPI(BACKEND_URL)

@app.route('/')
def index():
    """Main dashboard page."""
    # Get data from backend
    health_status = backend_api.get_health()
    indicators = backend_api.get_indicators()
    risks = backend_api.get_risks()
    insights = backend_api.get_insights()
    trends = backend_api.get_trends(lookback_days=7)
    
    return render_template('index.html', 
                         health_status=health_status,
                         indicators=indicators,
                         risks=risks,
                         insights=insights,
                         trends=trends)

@app.route('/indicators')
def indicators():
    """Indicators page."""
    indicators_data = backend_api.get_indicators()
    return render_template('indicators.html', indicators=indicators_data)

@app.route('/risks')
def risks():
    """Risks page."""
    risks_data = backend_api.get_risks()
    return render_template('risks.html', risks=risks_data)

@app.route('/insights')
def insights():
    """Insights page."""
    insights_data = backend_api.get_insights()
    return render_template('insights.html', insights=insights_data)

@app.route('/trends')
def trends():
    """Trends page."""
    data_type = request.args.get('type', 'all')
    lookback = request.args.get('lookback', 30)
    
    trends_data = backend_api.get_trends(data_type, int(lookback))
    return render_template('trends.html', 
                         trends=trends_data,
                         selected_type=data_type,
                         lookback_days=lookback)

@app.route('/pipeline')
def pipeline():
    """Pipeline control page."""
    return render_template('pipeline.html')

@app.route('/trigger/scrape', methods=['POST'])
def trigger_scrape():
    """Trigger scraping pipeline."""
    sources = request.form.getlist('sources')
    result = backend_api.trigger_scraping(sources)
    
    if result.get('status') == 'success':
        return jsonify({
            "status": "success", 
            "message": "Scraping started successfully",
            "task_id": result.get('data', {}).get('task_id')
        })
    else:
        return jsonify({
            "status": "error", 
            "message": result.get('error', 'Unknown error')
        }), 500

@app.route('/trigger/process', methods=['POST'])
def trigger_process():
    """Trigger processing pipeline."""
    result = backend_api.trigger_processing()
    
    if result.get('status') == 'success':
        return jsonify({
            "status": "success", 
            "message": "Processing started successfully",
            "task_id": result.get('data', {}).get('task_id')
        })
    else:
        return jsonify({
            "status": "error", 
            "message": result.get('error', 'Unknown error')
        }), 500

@app.route('/trigger/analyze', methods=['POST'])
def trigger_analyze():
    """Trigger analysis pipeline."""
    result = backend_api.trigger_analysis()
    
    if result.get('status') == 'success':
        return jsonify({
            "status": "success", 
            "message": "Analysis started successfully",
            "task_id": result.get('data', {}).get('task_id')
        })
    else:
        return jsonify({
            "status": "error", 
            "message": result.get('error', 'Unknown error')
        }), 500

@app.route('/health')
def health():
    """Health status page."""
    health_response = backend_api.get_health()
    queue_response = backend_api.get_queue_status(detailed=True)
    system_status_response = backend_api.get_system_status()
    
    # Format data for template
    system_status = {
        'overall_status': 'healthy' if health_response.get('status') == 'success' else 'unhealthy',
        'backend_status': health_response.get('data', {}).get('flask', 'unknown'),
        'database_status': health_response.get('data', {}).get('mongodb', 'unknown'),
        'queue_status': health_response.get('data', {}).get('celery', 'unknown'),
        'redis_status': health_response.get('data', {}).get('redis', 'unknown'),
        'uptime': 'N/A',  # Would need to be calculated from system start time
        'backend_version': '1.0.0',
        'database_collections': system_status_response.get('data', {}).get('system_status', {}).get('data_availability', {}),
        'queue_tasks': queue_response.get('data', {}).get('queues', {})
    }
    
    return render_template('health.html', 
                         system_status=system_status,
                         health_response=health_response,
                         queue_response=queue_response,
                         system_status_response=system_status_response)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    error_id = str(uuid.uuid4())
    request_id = request.headers.get('X-Request-ID', 'unknown')
    timestamp = datetime.utcnow().isoformat()
    return render_template('500.html', 
                         error_id=error_id, 
                         request_id=request_id, 
                         timestamp=timestamp), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
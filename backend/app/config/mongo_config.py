from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self, app=None):
        self.client = None
        self.db = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        try:
            # Build connection string
            if app.config['MONGODB_USERNAME'] and app.config['MONGODB_PASSWORD']:
                connection_string = f"mongodb://{app.config['MONGODB_USERNAME']}:{app.config['MONGODB_PASSWORD']}@{app.config['MONGODB_HOST']}:{app.config['MONGODB_PORT']}/?authSource=admin"
            else:
                connection_string = f"mongodb://{app.config['MONGODB_HOST']}:{app.config['MONGODB_PORT']}"
            
            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Test connection
            self.client.admin.command('ismaster')
            
            self.db = self.client[app.config['MONGODB_DB']]
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"Successfully connected to MongoDB: {app.config['MONGODB_DB']}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        # News collection indexes
        self.db.news.create_index([("published_at", -1)])
        self.db.news.create_index([("source", 1), ("published_at", -1)])
        self.db.news.create_index([("category", 1), ("published_at", -1)])
        
        # Trends collection indexes
        self.db.trends.create_index([("timestamp", -1)])
        self.db.trends.create_index([("keyword", 1), ("timestamp", -1)])
        
        # Weather collection indexes
        self.db.weather.create_index([("timestamp", -1)])
        self.db.weather.create_index([("location", 1), ("timestamp", -1)])
        
        # Food pricing indexes
        self.db.food_prices.create_index([("date", -1)])
        self.db.food_prices.create_index([("item", 1), ("date", -1)])
        
        # Tax revenue indexes
        self.db.tax_revenue.create_index([("period", -1)])
        
        # YouTube data indexes
        self.db.youtube_data.create_index([("published_at", -1)])
        self.db.youtube_data.create_index([("channel_id", 1), ("published_at", -1)])
        
        # Indicators indexes
        self.db.indicators.create_index([("timestamp", -1)])
        self.db.indicators.create_index([("type", 1), ("timestamp", -1)])
        
        # Risks indexes
        self.db.risks.create_index([("timestamp", -1)])
        self.db.risks.create_index([("severity", 1), ("timestamp", -1)])
        
        # Insights indexes
        self.db.insights.create_index([("created_at", -1)])
        self.db.insights.create_index([("category", 1), ("created_at", -1)])
    
    def get_collection(self, collection_name):
        if self.db is None:
            raise RuntimeError("MongoDB not initialized")
        return self.db[collection_name]
    
    def close_connection(self):
        if self.client:
            self.client.close()

# Global MongoDB instance
mongo = MongoDBManager()
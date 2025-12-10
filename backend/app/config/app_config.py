import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB Configuration
    MONGODB_HOST = os.environ.get('MONGODB_HOST', 'localhost')
    MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
    MONGODB_DB = os.environ.get('MONGODB_DB', 'situational_awareness')
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', '')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', '')
    
    # Redis Configuration for Celery
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Asia/Colombo'
    CELERY_ENABLE_UTC = True
    
    # API Configuration
    API_PREFIX = '/api/v1'
    
    # Scraper Configuration
    NEWS_SCRAPE_INTERVAL = timedelta(hours=1)
    TRENDS_SCRAPE_INTERVAL = timedelta(hours=6)
    WEATHER_SCRAPE_INTERVAL = timedelta(hours=3)
    PRICING_SCRAPE_INTERVAL = timedelta(days=1)
    
    # External API Keys (should be set as environment variables)
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')
    
    # ML Model Configuration
    ML_MODELS_DIR = os.path.join(os.path.dirname(__file__), '../../ml/models')
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    TESTING = True
    MONGODB_DB = 'test_situational_awareness'
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
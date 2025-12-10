from celery import Celery
from .app_config import Config
import logging

logger = logging.getLogger(__name__)

def make_celery(app_name=__name__):
    """Create and configure Celery application"""
    
    # Configure Celery with Redis as broker and result backend
    celery = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=[
            'app.service.tasks.scraping_tasks',
            'app.service.tasks.processing_tasks',
            'app.service.tasks.analysis_tasks'
        ]
    )
    
    # Celery configuration
    celery.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='Asia/Colombo',
        enable_utc=True,
        
        # Task queues
        task_queues={
            'scraping': {
                'exchange': 'scraping',
                'routing_key': 'scraping'
            },
            'processing': {
                'exchange': 'processing',
                'routing_key': 'processing'
            },
            'analysis': {
                'exchange': 'analysis',
                'routing_key': 'analysis'
            },
            'default': {
                'exchange': 'default',
                'routing_key': 'default'
            }
        },
        
        # Task routes
        task_routes={
            'app.service.tasks.scraping_tasks.*': {
                'queue': 'scraping',
                'routing_key': 'scraping'
            },
            'app.service.tasks.processing_tasks.*': {
                'queue': 'processing',
                'routing_key': 'processing'
            },
            'app.service.tasks.analysis_tasks.*': {
                'queue': 'analysis',
                'routing_key': 'analysis'
            }
        },
        
        # Worker settings
        worker_prefetch_multiplier=1,
        worker_concurrency=4,
        worker_max_tasks_per_child=1000,
        
        # Task timeouts
        task_time_limit=300,  # 5 minutes
        task_soft_time_limit=240,  # 4 minutes
        
        # Result expiration
        result_expires=3600,  # 1 hour
        
        # Beat schedule
        beat_schedule={
            'scrape-news-hourly': {
                'task': 'app.service.tasks.scraping_tasks.scrape_news_task',
                'schedule': 3600.0,  # Every hour
                'options': {'queue': 'scraping'}
            },
            'scrape-trends-daily': {
                'task': 'app.service.tasks.scraping_tasks.scrape_trends_task',
                'schedule': 86400.0,  # Every day
                'options': {'queue': 'scraping'}
            },
            'scrape-youtube-daily': {
                'task': 'app.service.tasks.scraping_tasks.scrape_youtube_task',
                'schedule': 86400.0,  # Every day
                'options': {'queue': 'scraping'}
            },
            'scrape-weather-hourly': {
                'task': 'app.service.tasks.scraping_tasks.scrape_weather_task',
                'schedule': 3600.0,  # Every hour
                'options': {'queue': 'scraping'}
            },
            'scrape-pricing-daily': {
                'task': 'app.service.tasks.scraping_tasks.scrape_pricing_task',
                'schedule': 86400.0,  # Every day
                'options': {'queue': 'scraping'}
            },
            'scrape-tax-monthly': {
                'task': 'app.service.tasks.scraping_tasks.scrape_tax_task',
                'schedule': 2592000.0,  # Every 30 days
                'options': {'queue': 'scraping'}
            },
            'process-data-hourly': {
                'task': 'app.service.tasks.processing_tasks.process_data_task',
                'schedule': 3600.0,  # Every hour
                'options': {'queue': 'processing'}
            },
            'analyze-data-daily': {
                'task': 'app.service.tasks.analysis_tasks.analyze_data_task',
                'schedule': 86400.0,  # Every day
                'options': {'queue': 'analysis'}
            },
            'cleanup-old-data-weekly': {
                'task': 'app.service.tasks.processing_tasks.cleanup_old_data_task',
                'schedule': 604800.0,  # Every week
                'options': {'queue': 'processing'}
            }
        },
        
        # Security settings
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        
        # Monitoring
        worker_send_task_events=True,
        task_send_sent_event=True
    )
    
    logger.info("Celery application configured successfully")
    return celery

# Create Celery application
celery = make_celery()

if __name__ == '__main__':
    celery.start()
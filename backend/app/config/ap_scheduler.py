from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

def AP_scheduler():
    try:
        # Method 1: Using APScheduler's ThreadPoolExecutor class directly
        executors = {
            'default': ThreadPoolExecutor(max_workers=20),
            'processpool': ProcessPoolExecutor(max_workers=5)
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 30
        }
        
        scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        return scheduler
    except Exception as e:
        print("AP Scheduler Error:", str(e))
        return None
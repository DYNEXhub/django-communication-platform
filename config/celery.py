"""
Celery configuration for Django Communication Platform.
Task queue setup for background jobs and scheduled tasks.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

# Create Celery app instance
app = Celery('communication_platform')

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app configs
app.autodiscover_tasks()


# Celery Beat Schedule (periodic tasks)
app.conf.beat_schedule = {
    'cleanup-old-sessions': {
        'task': 'apps.accounts.tasks.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'process-scheduled-campaigns': {
        'task': 'apps.campaigns.tasks.process_scheduled_campaigns',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'check-automation-triggers': {
        'task': 'apps.automations.tasks.check_automation_triggers',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'update-campaign-analytics': {
        'task': 'apps.campaigns.tasks.update_campaign_analytics',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task for testing Celery configuration.
    Usage: from config.celery import debug_task; debug_task.delay()
    """
    print(f'Request: {self.request!r}')

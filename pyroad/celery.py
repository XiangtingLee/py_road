from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyroad.settings')

app = Celery('pyroad', backend="redis", broker='redis://127.0.0.1:6379/1')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object('django.conf:settings')
# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)

app.conf.update(
    CELERYBEAT_SCHEDULE={
        'position-task-python': {
            'task': 'public.tasks.run_cache_delay_spider',
            'schedule': crontab(minute=0, hour="10,14,18,22"),
            'args': ("lg_position", ("全国", "Python"),)
        },
        'position-task-java': {
            'task': 'public.tasks.run_cache_delay_spider',
            'schedule': crontab(minute=10, hour="10,14,18,22"),
            'args': ("lg_position", ("全国", "Java"),)
        },
        'pneumonia-task': {
            'task': 'public.tasks.run_delay_spider',
            'schedule': timedelta(minutes=5),
            'args': ("COVID_data",)
        },
        'timeline-task': {
            'task': 'public.tasks.run_delay_spider',
            'schedule': timedelta(minutes=30),
            'args': ("COVID_timeline",)
        }
    }
)

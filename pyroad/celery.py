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
#app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object('django.conf:settings')
# Load task modules from all registered Django app configs.
app.autodiscover_tasks(settings.INSTALLED_APPS)

app.conf.update(
    CELERYBEAT_SCHEDULE = {
        'pneumonia-task': {
            'task': 'public.tasks.run_schedule',
            'schedule':  timedelta(minutes=1),
        }
    }
)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

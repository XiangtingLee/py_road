# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, Task

from log.models import SpiderRunLog
from position.views import update_position_visualization_cache

import logging
import datetime
import subprocess


class MyTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        update_position_visualization_cache(task_id)
        SpiderRunLog.objects.filter(task_id=task_id).update(status=True, end_time=datetime.datetime.now())
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)


@shared_task(base=MyTask)
def run_shell(command):
    logging.warning("start command %s" % command)
    subprocess.run(command, shell=True)
    logging.warning('command "%s" done' % command)


@shared_task
def run_schedule(command):
    logging.warning("start command %s" % command)
    subprocess.run(command, shell=True)
    logging.warning('command "%s" done' % command)

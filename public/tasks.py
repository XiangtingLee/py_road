from __future__ import absolute_import, unicode_literals

import os
import json
import base64
import logging
import datetime
import subprocess
from celery import shared_task, Task

from public.models.spider.spider import Spider
from log.models.spider_run import SpiderRunLog
from position import views as PositionViews

import os
import logging
import datetime
import subprocess


def delay_spider(spider_name, *args, **kwargs):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spider_path = Spider.objects.get(name=spider_name).path
    param = " -" + " -".join(args) if args else ""
    for k, v in kwargs.items():
        param += " --" + k + "=" + v
    command = "python3 " + base_dir + spider_path + param
    sync_task = run_shell.delay(command)
    SpiderRunLog.objects.create(spider_name=spider_name, task_id=sync_task.id, param=param)


class MyTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        SpiderRunLog.objects.filter(task_id=task_id).update(status=True, end_time=datetime.datetime.now())
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)


class CacheTask(MyTask):
    def on_success(self, retval, task_id, args, kwargs):
        PositionViews.update_position_visualization_cache(task_id)
        SpiderRunLog.objects.filter(task_id=task_id).update(status=True, end_time=datetime.datetime.now())
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)


@shared_task(base=MyTask)
def run_shell(command):
    logging.warning("start command %s" % command)
    subprocess.run(command, shell=True)
    logging.warning('command "%s" done' % command)


@shared_task
def run_schedule(command):
    logging.warning("Start command %s" % command)
    subprocess.run(command, shell=True)
    logging.warning('Command "%s" done' % command)


@shared_task(base=MyTask)
def run_delay_spider(spider_name, args=(), kwargs=None):
    if kwargs is None:
        kwargs = {}
    delay_spider(spider_name, *args, **kwargs)


@shared_task(base=CacheTask)
def run_cache_delay_spider(spider_name, args=(), kwargs=None):
    if kwargs is None:
        kwargs = {}
    delay_spider(spider_name, *args, **kwargs)

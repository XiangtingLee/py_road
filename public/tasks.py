# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

import logging
import subprocess


@shared_task
def run_shell(command):
    logging.warning("start command %s"%command)
    subprocess.run(command, shell=True)
    logging.warning('command "%s" done'%command)
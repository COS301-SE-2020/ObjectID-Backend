from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")


app = Celery('objectid')


app.config_from_object('django.conf:settings', namespace="CELERY")

app.autodiscover_tasks()

@app.task
def debug_task(self):
    print(f'Request: {self.request!r}')
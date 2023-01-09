import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MptApi.settings')

app = Celery('MptApi')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MptApi.settings')

app = Celery('MptApi')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'load-week': {
        'task': 'timetable.tasks.set_week',
        'schedule': crontab(minute='*/1')
    },
    'load-specialities': {
        'task': 'timetable.tasks.set_specialities',
        'schedule': crontab(minute='*/1')
    },
    'load-groups': {
        'task': 'timetable.tasks.set_groups',
        'schedule': crontab(minute='*/1')
    },
    'set_timetable': {
        'task': 'timetable.tasks.set_timetable',
        'schedule': crontab(minute='*/1')
    },
    'set_replacement': {
        'task': 'timetable.tasks.set_replacement',
        'schedule': crontab(minute='*/1')
    },
}
# celery -A MptApi worker -l info
# celery -A MptApi beat -l info
# docker exec -it zealous_faraday redis-cli

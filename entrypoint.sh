python manage.py runserver 0.0.0.0:21000
celery -A MptApi worker -l info
celery -A MptApi beat -l info
release: python manage.py migrate
web: gunicorn traitcuration.wsgi
worker: celery -A traitcuration worker -l info
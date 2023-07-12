import os
from django.core.wsgi import get_wsgi_application
from weather.cron import cron_weather

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuriggun.settings')

application = get_wsgi_application()

cron_weather()
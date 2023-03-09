import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core', broker=['redis://localhost:6379/1','redis://localhost:6379/2'])
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.beat_schedule = {
    'get_klines_3s': {
        'task':'trade.tasks.get_klines',
        'schedule': 60.0
    }
}

# app.conf.beat_schedule = {
#     'get_time_1s': {
#         'task':'trade.tasks.get_time',
#         'schedule': 1.0
#     }
# }
     
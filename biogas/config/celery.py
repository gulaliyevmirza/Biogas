import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('biogas')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ─── PERIODIC TASKS ───────────────────────────────────────────────────────────
app.conf.beat_schedule = {
    # Methan proqnozu hər 6 saatdan bir
    'predict-methane-every-6-hours': {
        'task': 'apps.analytics.tasks.predict_methane',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    # Günlük ekonomik hesabat
    'daily-economic-summary': {
        'task': 'apps.economic.tasks.generate_daily_summary',
        'schedule': crontab(minute=0, hour=23),
    },
    # Hər saat sensor anomaliya yoxlaması
    'check-sensor-anomalies': {
        'task': 'apps.sensors.tasks.check_all_sensor_thresholds',
        'schedule': crontab(minute=0),
    },
}

app.conf.timezone = 'Asia/Baku'

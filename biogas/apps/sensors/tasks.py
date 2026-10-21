import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('apps.sensors')


@shared_task(name='apps.sensors.tasks.check_all_sensor_thresholds')
def check_all_sensor_thresholds():
    """Hər saatda bir bütün sensorların son dəyərlərini yoxla"""
    from .models import Sensor, SensorData
    from apps.alerts.models import Alert
    from apps.alerts.tasks import send_critical_alert_email

    sensors = Sensor.objects.filter(is_active=True)
    checked = 0
    alerts_created = 0

    for sensor in sensors:
        latest = sensor.data_points.order_by('-timestamp').first()
        if not latest:
            continue
        # Son 1 saatdan köhnə isə keç
        if latest.timestamp < timezone.now() - timedelta(hours=1):
            continue
        status = sensor.check_threshold(latest.value)
        if status != 'normal':
            # Son 30 dəqiqədə eyni sensor üçün oxşar alert varmı?
            recent_alert = Alert.objects.filter(
                sensor=sensor,
                created_at__gte=timezone.now() - timedelta(minutes=30),
                severity=status,
            ).exists()
            if not recent_alert:
                alert = Alert.objects.create(
                    sensor=sensor,
                    message=(
                        f'[Saatlıq Yoxlama] Sensor "{sensor.name}" anormal dəyər: '
                        f'{latest.value} {sensor.unit}'
                    ),
                    severity=status,
                )
                alerts_created += 1
                if status == 'critical':
                    send_critical_alert_email.delay(alert.id)
        checked += 1

    logger.info(f'Threshold check: {checked} sensor yoxlandı, {alerts_created} alert yaradıldı.')
    return {'checked': checked, 'alerts_created': alerts_created}

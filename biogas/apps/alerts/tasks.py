import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger('apps.alerts')
User = get_user_model()


@shared_task(name='apps.alerts.tasks.send_critical_alert_email', bind=True, max_retries=3)
def send_critical_alert_email(self, alert_id):
    """Kritik alertlər üçün admin və mühendislərə email göndər"""
    from .models import Alert
    try:
        alert = Alert.objects.select_related('sensor').get(pk=alert_id)
        if alert.email_sent:
            return {'status': 'already_sent'}

        recipients = list(
            User.objects.filter(
                role__in=['admin', 'muhendis'],
                is_active=True,
                email__isnull=False
            ).exclude(email='').values_list('email', flat=True)
        )

        if not recipients:
            logger.warning('Kritik alert üçün alıcı tapılmadı.')
            return {'status': 'no_recipients'}

        subject = f'🚨 BioGas 4.0 - Kritik Xəbərdarlıq: {alert.sensor.name if alert.sensor else "Sistem"}'
        message = (
            f'Kritik xəbərdarlıq aşkarlandı!\n\n'
            f'Sensor: {alert.sensor.name if alert.sensor else "N/A"}\n'
            f'Ciddilik: {alert.get_severity_display()}\n'
            f'Mesaj: {alert.message}\n'
            f'Zaman: {alert.created_at.strftime("%d.%m.%Y %H:%M:%S")}\n\n'
            f'Platforma admin panelinə daxil olaraq tədbirlər görün.\n'
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )

        alert.email_sent = True
        alert.save(update_fields=['email_sent'])
        logger.info(f'Alert #{alert_id} üçün email göndərildi: {recipients}')
        return {'status': 'sent', 'recipients': len(recipients)}

    except Alert.DoesNotExist:
        logger.error(f'Alert #{alert_id} tapılmadı.')
        return {'status': 'not_found'}
    except Exception as exc:
        logger.error(f'Email göndərmə xətası: {exc}')
        raise self.retry(exc=exc, countdown=60)

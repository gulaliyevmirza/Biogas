from django.db import models


class Alert(models.Model):
    class Severity(models.TextChoices):
        INFO = 'info', 'Məlumat'
        WARNING = 'warning', 'Xəbərdarlıq'
        CRITICAL = 'critical', 'Kritik'

    sensor = models.ForeignKey(
        'sensors.Sensor',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='alerts',
        verbose_name='Sensor'
    )
    message = models.TextField(verbose_name='Mesaj')
    severity = models.CharField(
        max_length=10, choices=Severity.choices,
        default=Severity.INFO, verbose_name='Ciddilik dərəcəsi'
    )
    is_read = models.BooleanField(default=False, verbose_name='Oxunub')
    email_sent = models.BooleanField(default=False, verbose_name='Email göndərilib')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Xəbərdarlıq'
        verbose_name_plural = 'Xəbərdarlıqlar'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]

    def __str__(self):
        return f'[{self.get_severity_display()}] {self.message[:60]}'

    def mark_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])

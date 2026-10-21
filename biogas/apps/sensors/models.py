from django.db import models
from django.utils import timezone


class Sensor(models.Model):
    class SensorType(models.TextChoices):
        TEMPERATURE = 'temperature', 'Temperatur'
        PH = 'pH', 'pH'
        CH4 = 'CH4', 'Metan (CH4)'
        CO2 = 'CO2', 'Karbon Dioksid (CO2)'
        H2S = 'H2S', 'Hidrogen Sulfid (H2S)'
        ORP = 'ORP', 'Oksidləşmə-Reduksiya Potensialı (ORP)'
        PRESSURE = 'pressure', 'Təzyiq'
        FLOW = 'flow', 'Axın sürəti'

    name = models.CharField(max_length=200, verbose_name='Ad')
    type = models.CharField(
        max_length=20, choices=SensorType.choices, verbose_name='Növ'
    )
    unit = models.CharField(max_length=50, verbose_name='Ölçü vahidi')
    location = models.CharField(max_length=200, verbose_name='Yerləşmə')
    threshold_min = models.FloatField(
        null=True, blank=True, verbose_name='Minimum hədd'
    )
    threshold_max = models.FloatField(
        null=True, blank=True, verbose_name='Maksimum hədd'
    )
    is_active = models.BooleanField(default=True, verbose_name='Aktivdir')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensorlar'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_type_display()}) - {self.location}'

    def check_threshold(self, value):
        """Returns 'normal', 'warning', or 'critical' based on value vs thresholds"""
        if self.threshold_min is not None and value < self.threshold_min:
            deviation = abs(value - self.threshold_min) / (self.threshold_min + 1e-9)
            return 'critical' if deviation > 0.2 else 'warning'
        if self.threshold_max is not None and value > self.threshold_max:
            deviation = abs(value - self.threshold_max) / (self.threshold_max + 1e-9)
            return 'critical' if deviation > 0.2 else 'warning'
        return 'normal'


class SensorData(models.Model):
    sensor = models.ForeignKey(
        Sensor, on_delete=models.CASCADE,
        related_name='data_points', verbose_name='Sensor'
    )
    value = models.FloatField(verbose_name='Dəyər')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='Zaman damğası')
    is_anomaly = models.BooleanField(default=False, verbose_name='Anomaliyadır')

    class Meta:
        verbose_name = 'Sensor Datası'
        verbose_name_plural = 'Sensor Dataları'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]

    def __str__(self):
        return f'{self.sensor.name}: {self.value} {self.sensor.unit} @ {self.timestamp}'

    def save(self, *args, **kwargs):
        status = self.sensor.check_threshold(self.value)
        self.is_anomaly = status != 'normal'
        super().save(*args, **kwargs)
        # Trigger alert creation if anomaly
        if self.is_anomaly:
            self._create_alert(status)

    def _create_alert(self, severity):
        from apps.alerts.models import Alert
        from apps.alerts.tasks import send_critical_alert_email
        alert = Alert.objects.create(
            sensor=self.sensor,
            message=(
                f'Sensor "{self.sensor.name}" anormal dəyər qeydə alındı: '
                f'{self.value} {self.sensor.unit}. '
                f'Hədd: [{self.sensor.threshold_min}, {self.sensor.threshold_max}]'
            ),
            severity=severity,
        )
        if severity == 'critical':
            send_critical_alert_email.delay(alert.id)

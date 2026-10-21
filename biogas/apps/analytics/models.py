from django.db import models
from django.utils import timezone


class ProductionLog(models.Model):
    date = models.DateField(default=timezone.now, verbose_name='Tarix', unique=True)
    methane_output = models.FloatField(verbose_name='Metan çıxışı (m³)')
    biogas_output = models.FloatField(verbose_name='Biogaz çıxışı (m³)')
    energy_generated = models.FloatField(verbose_name='Yaradılan enerji (kWh)')
    co2_reduction = models.FloatField(verbose_name='CO2 azalması (kq)')
    temperature_avg = models.FloatField(verbose_name='Orta temperatur (°C)')
    ph_avg = models.FloatField(verbose_name='Orta pH')
    feedstock_used = models.FloatField(
        default=0, verbose_name='İstifadə edilən xammal (kq)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'İstehsal Jurnalı'
        verbose_name_plural = 'İstehsal Jurnalları'
        ordering = ['-date']

    def __str__(self):
        return f'İstehsal: {self.date} — {self.methane_output} m³ CH4'


class AIPrediction(models.Model):
    prediction_date = models.DateTimeField(default=timezone.now, verbose_name='Proqnoz tarixi')
    predicted_methane_24h = models.FloatField(verbose_name='24s proqnozu (m³)')
    predicted_methane_48h = models.FloatField(verbose_name='48s proqnozu (m³)')
    predicted_methane_72h = models.FloatField(verbose_name='72s proqnozu (m³)')
    confidence_score = models.FloatField(verbose_name='Etibar skoru (0-1)')
    recommendations = models.JSONField(default=list, verbose_name='Tövsiyələr')
    model_version = models.CharField(max_length=50, default='v1.0', verbose_name='Model versiyası')
    data_points_used = models.IntegerField(default=0, verbose_name='İstifadə edilən data nöqtələri')

    class Meta:
        verbose_name = 'AI Proqnozu'
        verbose_name_plural = 'AI Proqnozları'
        ordering = ['-prediction_date']

    def __str__(self):
        return f'Proqnoz {self.prediction_date.strftime("%d.%m.%Y %H:%M")} — 24s: {self.predicted_methane_24h:.1f} m³'

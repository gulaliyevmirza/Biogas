from django.db import models
from django.utils import timezone


class ProcessOptimization(models.Model):
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Yaradılma vaxtı')
    parameter_name = models.CharField(max_length=200, verbose_name='Parametr adı')
    current_value = models.FloatField(verbose_name='Cari dəyər')
    recommended_value = models.FloatField(verbose_name='Tövsiyə olunan dəyər')
    unit = models.CharField(max_length=50, blank=True, verbose_name='Vahid')
    reason = models.TextField(verbose_name='Səbəb')
    applied = models.BooleanField(default=False, verbose_name='Tətbiq edildi')
    applied_at = models.DateTimeField(null=True, blank=True, verbose_name='Tətbiq vaxtı')
    applied_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='applied_optimizations',
        verbose_name='Tətbiq edən'
    )
    priority = models.CharField(
        max_length=10,
        choices=[('low', 'Aşağı'), ('medium', 'Orta'), ('high', 'Yüksək')],
        default='medium',
        verbose_name='Prioritet'
    )

    class Meta:
        verbose_name = 'Proses Optimallaşdırması'
        verbose_name_plural = 'Proses Optimallaşdırmaları'
        ordering = ['-created_at']

    def __str__(self):
        status = '✓' if self.applied else '○'
        return f'{status} {self.parameter_name}: {self.current_value} → {self.recommended_value}'

    def apply(self, user=None):
        self.applied = True
        self.applied_at = timezone.now()
        if user:
            self.applied_by = user
        self.save(update_fields=['applied', 'applied_at', 'applied_by'])

from django.db import models
from django.utils import timezone


class EconomicData(models.Model):
    date = models.DateField(default=timezone.now, unique=True, verbose_name='Tarix')
    revenue_gas = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Qaz gəliri (AZN)'
    )
    revenue_fertilizer = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Gübrə gəliri (AZN)'
    )
    revenue_other = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Digər gəlirlər (AZN)'
    )
    total_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Ümumi gəlir (AZN)'
    )
    expenses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Xərclər (AZN)'
    )
    net_profit = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Xalis mənfəət (AZN)'
    )
    roi_percentage = models.FloatField(default=0, verbose_name='ROI (%)')
    notes = models.TextField(blank=True, verbose_name='Qeydlər')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'İqtisadi Göstərici'
        verbose_name_plural = 'İqtisadi Göstəricilər'
        ordering = ['-date']

    def __str__(self):
        return f'İqtisadi data: {self.date} — Mənfəət: {self.net_profit} AZN'

    def save(self, *args, **kwargs):
        # Avtomatik hesabla
        self.total_revenue = self.revenue_gas + self.revenue_fertilizer + self.revenue_other
        self.net_profit = self.total_revenue - self.expenses
        if self.expenses > 0:
            self.roi_percentage = float(self.net_profit / self.expenses * 100)
        super().save(*args, **kwargs)

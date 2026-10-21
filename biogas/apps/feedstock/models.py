from django.db import models
from django.utils import timezone


class Feedstock(models.Model):
    class FeedType(models.TextChoices):
        GRAPE = 'grape', 'Üzüm tullantısı'
        POMEGRANATE = 'pomegranate', 'Nar tullantısı'
        APPLE = 'apple', 'Alma tullantısı'
        PEAR = 'pear', 'Armud tullantısı'
        PLUM = 'plum', 'Gavalı tullantısı'
        PUMPKIN = 'pumpkin', 'Balqabaq tullantısı'
        PEACH = 'peach', 'Şəftəli tullantısı'
        YEAST = 'yeast', 'Maya'
        MIXED = 'mixed', 'Qarışıq'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Gözləyir'
        PROCESSING = 'processing', 'Emal edilir'
        COMPLETED = 'completed', 'Tamamlandı'
        REJECTED = 'rejected', 'Rədd edildi'

    type = models.CharField(
        max_length=20, choices=FeedType.choices, verbose_name='Növ'
    )
    quantity = models.FloatField(verbose_name='Miqdar (kq)')
    received_date = models.DateField(default=timezone.now, verbose_name='Qəbul tarixi')
    status = models.CharField(
        max_length=15, choices=Status.choices,
        default=Status.PENDING, verbose_name='Status'
    )
    notes = models.TextField(blank=True, verbose_name='Qeydlər')
    supplier = models.CharField(max_length=200, blank=True, verbose_name='Tədarükçü')
    moisture_content = models.FloatField(
        null=True, blank=True, verbose_name='Nəmlik (%)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Xammal'
        verbose_name_plural = 'Xammallar'
        ordering = ['-received_date']
        indexes = [
            models.Index(fields=['-received_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'{self.get_type_display()} - {self.quantity} kq ({self.received_date})'


class Digestate(models.Model):
    class QualityGrade(models.TextChoices):
        A = 'A', 'A dərəcəsi (Premium)'
        B = 'B', 'B dərəcəsi (Standart)'
        C = 'C', 'C dərəcəsi (Əsas)'

    production_date = models.DateField(default=timezone.now, verbose_name='İstehsal tarixi')
    quantity = models.FloatField(verbose_name='Miqdar (ton)')
    quality_grade = models.CharField(
        max_length=1, choices=QualityGrade.choices,
        default=QualityGrade.B, verbose_name='Keyfiyyət dərəcəsi'
    )
    price_per_ton = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Ton başına qiymət (AZN)'
    )
    sold = models.BooleanField(default=False, verbose_name='Satıldı')
    sold_date = models.DateField(null=True, blank=True, verbose_name='Satış tarixi')
    buyer = models.CharField(max_length=200, blank=True, verbose_name='Alıcı')
    nitrogen_content = models.FloatField(
        null=True, blank=True, verbose_name='Azot miqdarı (%)'
    )
    phosphorus_content = models.FloatField(
        null=True, blank=True, verbose_name='Fosfor miqdarı (%)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Digestat (Gübrə)'
        verbose_name_plural = 'Digestatlar (Gübrələr)'
        ordering = ['-production_date']

    def __str__(self):
        return f'Digestat {self.production_date} - {self.quantity}t [{self.quality_grade}]'

    @property
    def total_value(self):
        return float(self.price_per_ton) * self.quantity

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('apps.economic')


@shared_task(name='apps.economic.tasks.generate_daily_summary')
def generate_daily_summary():
    """Hər gün gecə saat 23:00-da günlük iqtisadi hesabat yaradır"""
    from .models import EconomicData
    from apps.analytics.models import ProductionLog

    yesterday = (timezone.now() - timedelta(days=1)).date()

    if EconomicData.objects.filter(date=yesterday).exists():
        logger.info(f'{yesterday} üçün iqtisadi data artıq mövcuddur.')
        return {'status': 'already_exists'}

    prod = ProductionLog.objects.filter(date=yesterday).first()
    if not prod:
        logger.warning(f'{yesterday} üçün istehsal jurnalı tapılmadı.')
        return {'status': 'no_production_log'}

    # Sadə hesablamalar (real layihədə bunlar konfiqurə edilə bilər)
    GAS_PRICE_PER_M3 = 0.35  # AZN
    ENERGY_PRICE_PER_KWH = 0.12  # AZN

    revenue_gas = prod.biogas_output * GAS_PRICE_PER_M3
    revenue_energy = prod.energy_generated * ENERGY_PRICE_PER_KWH

    from apps.feedstock.models import Digestate
    digestate_revenue = sum(
        float(d.price_per_ton) * d.quantity
        for d in Digestate.objects.filter(sold_date=yesterday)
    )

    record = EconomicData.objects.create(
        date=yesterday,
        revenue_gas=revenue_gas + revenue_energy,
        revenue_fertilizer=digestate_revenue,
        expenses=100,  # Placeholder — real layihədə xərclər ayrı idarə olunur
        notes=f'Avtomatik yaradıldı: {timezone.now().strftime("%d.%m.%Y %H:%M")}'
    )
    logger.info(f'Günlük iqtisadi hesabat yaradıldı: {record}')
    return {'status': 'created', 'id': record.id, 'date': str(yesterday)}

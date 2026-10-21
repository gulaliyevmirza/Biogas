import logging
import numpy as np
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('apps.analytics')


@shared_task(name='apps.analytics.tasks.predict_methane', bind=True, max_retries=2)
def predict_methane(self):
    """
    Hər 6 saatdan bir işlər.
    Son 7 günün CH4 sensor datasına əsasən metan proqnozu hesablayır.
    Sadə istatistik model (trend + mevsimsellik) + konfigurə edilə bilən xarici AI API.
    """
    from apps.sensors.models import Sensor, SensorData
    from .models import AIPrediction

    try:
        # CH4 sensorlarını tap
        ch4_sensors = Sensor.objects.filter(type='CH4', is_active=True)
        if not ch4_sensors.exists():
            logger.warning('Aktiv CH4 sensoru tapılmadı, proqnoz dayandırıldı.')
            return {'status': 'no_sensors'}

        seven_days_ago = timezone.now() - timedelta(days=7)
        data_points = SensorData.objects.filter(
            sensor__in=ch4_sensors,
            timestamp__gte=seven_days_ago,
            is_anomaly=False,
        ).order_by('timestamp').values_list('value', 'timestamp')

        values = [dp[0] for dp in data_points]
        count = len(values)

        if count < 10:
            logger.warning(f'Kifayət qədər data yoxdur: {count} nöqtə.')
            return {'status': 'insufficient_data', 'count': count}

        # ─── Sadə statistik proqnoz modeli ──────────────────────────────────
        arr = np.array(values)

        # Son 24 saatın ortalaması — ağırlıqlı son dəyərlərə üstünlük ver
        recent = arr[-min(24, len(arr)):]
        weights = np.linspace(0.5, 1.5, len(recent))
        weighted_mean = np.average(recent, weights=weights)

        # Trend: son 48 saatın xətti regresiyası
        if len(arr) >= 48:
            x = np.arange(len(arr[-48:]))
            y = arr[-48:]
            slope = np.polyfit(x, y, 1)[0]
        else:
            slope = 0.0

        # Proqnozlar: ağırlıqlı ortalama + trend
        hours_per_step = 6  # Task hər 6 saatda işləyir
        pred_24h = max(0.0, weighted_mean + slope * (24 / hours_per_step))
        pred_48h = max(0.0, weighted_mean + slope * (48 / hours_per_step))
        pred_72h = max(0.0, weighted_mean + slope * (72 / hours_per_step))

        # Etibar skoru: data miqdarı + variasiya əsasında
        cv = np.std(recent) / (np.mean(recent) + 1e-9)  # Variasiya koeffisienti
        confidence = max(0.3, min(0.95, 1.0 - cv * 0.5)) * min(1.0, count / 100)

        # Tövsiyələr yarat
        recommendations = _generate_recommendations(arr, slope, weighted_mean, cv)

        prediction = AIPrediction.objects.create(
            predicted_methane_24h=round(pred_24h, 2),
            predicted_methane_48h=round(pred_48h, 2),
            predicted_methane_72h=round(pred_72h, 2),
            confidence_score=round(confidence, 3),
            recommendations=recommendations,
            data_points_used=count,
            model_version='statistical_v1.2',
        )

        logger.info(
            f'Metan proqnozu tamamlandı — 24s: {pred_24h:.2f} m³, '
            f'48s: {pred_48h:.2f} m³, etibar: {confidence:.2%}'
        )
        return {
            'status': 'success',
            'prediction_id': prediction.id,
            '24h': pred_24h,
            '48h': pred_48h,
            '72h': pred_72h,
            'confidence': confidence,
        }

    except Exception as exc:
        logger.error(f'Metan proqnozu xətası: {exc}', exc_info=True)
        raise self.retry(exc=exc, countdown=300)


def _generate_recommendations(arr, slope, mean, cv):
    """Statistik analizə əsasən tövsiyələr yarat"""
    recommendations = []

    if slope < -0.5:
        recommendations.append({
            'type': 'warning',
            'message': 'Metan istehsalında azalma trendi aşkarlandı. Xammal miqdarını artırın.',
            'priority': 'high',
        })
    elif slope > 0.5:
        recommendations.append({
            'type': 'info',
            'message': 'Metan istehsalı artım trendi göstərir. Hazırkı şəraiti qoruyun.',
            'priority': 'low',
        })

    if cv > 0.3:
        recommendations.append({
            'type': 'warning',
            'message': f'Metan çıxışında yüksək variasiya ({cv:.1%}). pH və temperatur sabitliyini yoxlayın.',
            'priority': 'medium',
        })

    if mean < 10:
        recommendations.append({
            'type': 'critical',
            'message': f'Orta metan çıxışı aşağıdır ({mean:.1f} m³). Fermentasiya prosesini yoxlayın.',
            'priority': 'high',
        })

    if not recommendations:
        recommendations.append({
            'type': 'info',
            'message': 'Bütün göstəricilər normal çərçivədədir. Sistem optimal işləyir.',
            'priority': 'low',
        })

    return recommendations

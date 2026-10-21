import logging
from django.utils import timezone
from django.db.models import Avg, Sum
from datetime import timedelta, date
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import ProductionLog, AIPrediction
from .serializers import (
    ProductionLogSerializer,
    AIPredictionSerializer,
    DailyReportSerializer,
)

logger = logging.getLogger('apps.analytics')


class ProductionLogViewSet(viewsets.ModelViewSet):
    queryset = ProductionLog.objects.all()
    serializer_class = ProductionLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['date']
    ordering_fields = ['date', 'methane_output', 'energy_generated']


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_live(self, request):
        """GET /api/analytics/live/ - Canlı göstəricilər"""
        from apps.sensors.models import Sensor, SensorData
        from apps.alerts.models import Alert

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Son sensor dəyərləri
        def get_latest(sensor_type):
            sensor = Sensor.objects.filter(type=sensor_type, is_active=True).first()
            if not sensor:
                return None
            latest = sensor.data_points.first()
            return latest.value if latest else None

        # Bu günkü istehsal
        today_log = ProductionLog.objects.filter(date=now.date()).first()

        # Aktiv alertlər
        active_alerts = Alert.objects.filter(is_read=False).count()

        # Sensor statusları
        sensors = Sensor.objects.filter(is_active=True)
        sensor_statuses = []
        for s in sensors:
            latest = s.data_points.first()
            sensor_statuses.append({
                'id': s.id,
                'name': s.name,
                'type': s.type,
                'value': latest.value if latest else None,
                'unit': s.unit,
                'status': s.check_threshold(latest.value) if latest else 'no_data',
            })

        return Response({
            'timestamp': now,
            'methane_current': get_latest('CH4'),
            'temperature_current': get_latest('temperature'),
            'ph_current': get_latest('pH'),
            'co2_current': get_latest('CO2'),
            'h2s_current': get_latest('H2S'),
            'biogas_today': today_log.biogas_output if today_log else 0,
            'energy_today': today_log.energy_generated if today_log else 0,
            'active_alerts': active_alerts,
            'sensor_statuses': sensor_statuses,
        })

    def get_history(self, request):
        """GET /api/analytics/history/?start=&end="""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if not start or not end:
            return Response(
                {'detail': 'start və end parametrləri tələb olunur.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        logs = ProductionLog.objects.filter(date__range=[start, end]).order_by('date')
        serializer = ProductionLogSerializer(logs, many=True)
        return Response({'data': serializer.data, 'count': logs.count()})

    def get_methane_prediction(self, request):
        """GET /api/analytics/methane-prediction/ - Son AI proqnozu"""
        prediction = AIPrediction.objects.first()
        if not prediction:
            return Response(
                {'detail': 'Hələ heç bir proqnoz mövcud deyil.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(AIPredictionSerializer(prediction).data)

    def get_daily_report(self, request):
        """GET /api/analytics/daily-report/?date=YYYY-MM-DD"""
        from apps.sensors.models import SensorData
        from apps.alerts.models import Alert
        from apps.feedstock.models import Feedstock

        report_date_str = request.query_params.get('date')
        try:
            report_date = date.fromisoformat(report_date_str) if report_date_str else date.today()
        except ValueError:
            return Response({'detail': 'Yanlış tarix formatı. YYYY-MM-DD istifadə edin.'}, status=400)

        log = ProductionLog.objects.filter(date=report_date).first()

        # Sensor ortalamaları
        day_start = timezone.make_aware(
            timezone.datetime.combine(report_date, timezone.datetime.min.time())
        )
        day_end = day_start + timedelta(days=1)
        averages = SensorData.objects.filter(
            timestamp__range=[day_start, day_end]
        ).values('sensor__type').annotate(avg=Avg('value'))

        sensor_avgs = {item['sensor__type']: round(item['avg'], 3) for item in averages}

        # Alert sayı
        alert_count = Alert.objects.filter(
            created_at__range=[day_start, day_end]
        ).count()

        # Qəbul edilən xammal
        feedstock_qty = Feedstock.objects.filter(
            received_date=report_date
        ).aggregate(total=Sum('quantity'))['total'] or 0

        return Response({
            'date': report_date,
            'production': ProductionLogSerializer(log).data if log else None,
            'sensor_averages': sensor_avgs,
            'alert_count': alert_count,
            'feedstock_received': feedstock_qty,
        })

    def get_monthly_report(self, request):
        """GET /api/analytics/monthly-report/?month=YYYY-MM"""
        month_str = request.query_params.get('month')
        if not month_str:
            now = timezone.now()
            year, month = now.year, now.month
        else:
            try:
                year, month = map(int, month_str.split('-'))
            except ValueError:
                return Response({'detail': 'Yanlış format. YYYY-MM istifadə edin.'}, status=400)

        logs = ProductionLog.objects.filter(date__year=year, date__month=month)
        agg = logs.aggregate(
            total_methane=Sum('methane_output'),
            total_biogas=Sum('biogas_output'),
            total_energy=Sum('energy_generated'),
            total_co2=Sum('co2_reduction'),
            avg_temp=Avg('temperature_avg'),
            avg_ph=Avg('ph_avg'),
        )
        return Response({
            'month': f'{year}-{month:02d}',
            'total_methane': round(agg['total_methane'] or 0, 2),
            'total_biogas': round(agg['total_biogas'] or 0, 2),
            'total_energy': round(agg['total_energy'] or 0, 2),
            'total_co2_reduction': round(agg['total_co2'] or 0, 2),
            'avg_temperature': round(agg['avg_temp'] or 0, 2),
            'avg_ph': round(agg['avg_ph'] or 0, 2),
            'production_days': logs.count(),
            'daily_breakdown': ProductionLogSerializer(logs.order_by('date'), many=True).data,
        })

    def get(self, request, *args, **kwargs):
        action = kwargs.get('action')
        dispatch = {
            'live': self.get_live,
            'history': self.get_history,
            'methane-prediction': self.get_methane_prediction,
            'daily-report': self.get_daily_report,
            'monthly-report': self.get_monthly_report,
        }
        handler = dispatch.get(action)
        if handler:
            return handler(request)
        return Response({'detail': 'Yanlış endpoint.'}, status=status.HTTP_404_NOT_FOUND)

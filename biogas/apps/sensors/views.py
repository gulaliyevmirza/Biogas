import logging
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Sensor, SensorData
from .serializers import (
    SensorSerializer,
    SensorDataSerializer,
    BulkDataIngestionSerializer,
)

logger = logging.getLogger('apps.sensors')


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'is_active', 'location']
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'type', 'created_at']

    @action(detail=True, methods=['get'], url_path='data')
    def sensor_data(self, request, pk=None):
        """GET /api/sensors/{id}/data/ - Get data for a specific sensor"""
        sensor = self.get_object()
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        limit = int(request.query_params.get('limit', 100))

        qs = SensorData.objects.filter(sensor=sensor)
        if start:
            qs = qs.filter(timestamp__gte=start)
        if end:
            qs = qs.filter(timestamp__lte=end)

        qs = qs.order_by('-timestamp')[:limit]
        serializer = SensorDataSerializer(qs, many=True)
        return Response({
            'sensor': SensorSerializer(sensor).data,
            'count': len(serializer.data),
            'data': serializer.data,
        })

    @action(detail=False, methods=['post'], url_path='data/bulk')
    def bulk_ingest(self, request):
        """POST /api/sensors/data/bulk/ - Bulk data ingestion from IoT devices"""
        serializer = BulkDataIngestionSerializer(data=request.data)
        if serializer.is_valid():
            created = serializer.save()
            logger.info(f'Bulk ingestion: {len(created)} data points received.')
            return Response(
                {'created': len(created), 'status': 'success'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='live')
    def live(self, request):
        """GET /api/sensors/live/ - Latest value from each active sensor"""
        sensors = Sensor.objects.filter(is_active=True)
        result = []
        for sensor in sensors:
            latest = sensor.data_points.first()
            result.append({
                'id': sensor.id,
                'name': sensor.name,
                'type': sensor.type,
                'unit': sensor.unit,
                'location': sensor.location,
                'value': latest.value if latest else None,
                'timestamp': latest.timestamp if latest else None,
                'status': sensor.check_threshold(latest.value) if latest else 'no_data',
                'threshold_min': sensor.threshold_min,
                'threshold_max': sensor.threshold_max,
            })
        return Response(result)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['severity', 'is_read', 'sensor']

    def get_queryset(self):
        qs = Alert.objects.select_related('sensor').all()
        # Default: sadəcə oxunmamışlar
        if self.action == 'list':
            show_all = self.request.query_params.get('all', '0')
            if show_all != '1':
                qs = qs.filter(is_read=False)
        return qs

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        alert = self.get_object()
        alert.mark_read()
        return Response({'status': 'oxundu', 'id': alert.id})

    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_read(self, request):
        count = Alert.objects.filter(is_read=False).update(is_read=True)
        return Response({'status': 'hamısı oxundu', 'count': count})

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """GET /api/alerts/history/ - Bütün alertlər (oxunmuş + oxunmamış)"""
        qs = Alert.objects.select_related('sensor').all()
        severity = request.query_params.get('severity')
        if severity:
            qs = qs.filter(severity=severity)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        from django.db.models import Count
        stats = Alert.objects.values('severity').annotate(
            total=Count('id'),
            unread=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(is_read=False))
        )
        return Response(list(stats))

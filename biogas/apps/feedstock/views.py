from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Feedstock, Digestate
from .serializers import (
    FeedstockSerializer,
    FeedstockStatusUpdateSerializer,
    DigestateSerializer,
    DigestateSellSerializer,
)


class FeedstockViewSet(viewsets.ModelViewSet):
    queryset = Feedstock.objects.all()
    serializer_class = FeedstockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type', 'status']
    search_fields = ['supplier', 'notes']
    ordering_fields = ['received_date', 'quantity']

    @action(detail=True, methods=['put', 'patch'], url_path='status')
    def update_status(self, request, pk=None):
        feedstock = self.get_object()
        serializer = FeedstockStatusUpdateSerializer(
            feedstock, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(FeedstockSerializer(feedstock).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        from django.db.models import Sum, Count
        summary = Feedstock.objects.values('type', 'status').annotate(
            total_qty=Sum('quantity'),
            count=Count('id')
        )
        return Response(list(summary))


class DigestateViewSet(viewsets.ModelViewSet):
    queryset = Digestate.objects.all()
    serializer_class = DigestateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['quality_grade', 'sold']
    ordering_fields = ['production_date', 'quantity']

    @action(detail=True, methods=['post'], url_path='sell')
    def sell(self, request, pk=None):
        digestate = self.get_object()
        if digestate.sold:
            return Response(
                {'detail': 'Bu digestat artıq satılıb.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DigestateSellSerializer(digestate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(sold=True)
            return Response(DigestateSerializer(digestate).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

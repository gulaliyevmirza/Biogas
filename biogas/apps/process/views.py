from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ProcessOptimization
from .serializers import ProcessOptimizationSerializer


class ProcessOptimizationViewSet(viewsets.ModelViewSet):
    queryset = ProcessOptimization.objects.all()
    serializer_class = ProcessOptimizationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['applied', 'priority']
    ordering_fields = ['created_at', 'priority']

    @action(detail=False, methods=['get'], url_path='latest')
    def latest(self, request):
        """GET /api/process/optimization/latest/ - Tətbiq edilməmiş optimallaşdırmalar"""
        qs = self.get_queryset().filter(applied=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='apply')
    def apply_optimization(self, request, pk=None):
        """POST /api/process/apply-optimization/{id}/"""
        opt = self.get_object()
        if opt.applied:
            return Response(
                {'detail': 'Bu optimallaşdırma artıq tətbiq edilib.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        opt.apply(user=request.user)
        return Response(self.get_serializer(opt).data)

    @action(detail=False, methods=['get'], url_path='logs')
    def logs(self, request):
        """GET /api/process/logs/ - Tətbiq edilmiş optimallaşdırmalar"""
        qs = self.get_queryset().filter(applied=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(qs, many=True).data)

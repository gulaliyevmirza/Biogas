from django.utils import timezone
from django.db.models import Sum, Avg
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import EconomicData
from .serializers import EconomicDataSerializer


class EconomicDataViewSet(viewsets.ModelViewSet):
    queryset = EconomicData.objects.all()
    serializer_class = EconomicDataSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['date']
    ordering_fields = ['date', 'net_profit', 'total_revenue']

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """GET /api/economic/summary/?period=day|week|month|year"""
        period = request.query_params.get('period', 'month')
        now = timezone.now().date()

        period_map = {
            'day': now - timedelta(days=1),
            'week': now - timedelta(weeks=1),
            'month': now - timedelta(days=30),
            'year': now - timedelta(days=365),
        }
        start_date = period_map.get(period, period_map['month'])
        qs = EconomicData.objects.filter(date__gte=start_date)
        agg = qs.aggregate(
            total_revenue=Sum('total_revenue'),
            total_expenses=Sum('expenses'),
            total_net_profit=Sum('net_profit'),
            avg_roi=Avg('roi_percentage'),
            revenue_gas=Sum('revenue_gas'),
            revenue_fertilizer=Sum('revenue_fertilizer'),
        )
        return Response({
            'period': period,
            'start_date': start_date,
            'end_date': now,
            'total_revenue': agg['total_revenue'] or 0,
            'total_expenses': agg['total_expenses'] or 0,
            'total_net_profit': agg['total_net_profit'] or 0,
            'avg_roi': round(agg['avg_roi'] or 0, 2),
            'revenue_gas': agg['revenue_gas'] or 0,
            'revenue_fertilizer': agg['revenue_fertilizer'] or 0,
            'data_points': qs.count(),
        })

    @action(detail=False, methods=['get'], url_path='revenue-breakdown')
    def revenue_breakdown(self, request):
        """GET /api/economic/revenue-breakdown/"""
        period = request.query_params.get('period', 'month')
        now = timezone.now().date()
        start = now - timedelta(days=30 if period == 'month' else 365)
        qs = EconomicData.objects.filter(date__gte=start)
        agg = qs.aggregate(
            gas=Sum('revenue_gas'),
            fertilizer=Sum('revenue_fertilizer'),
            other=Sum('revenue_other'),
            total=Sum('total_revenue'),
        )
        total = float(agg['total'] or 1)
        return Response({
            'gas': {'amount': agg['gas'] or 0, 'percentage': round(float(agg['gas'] or 0) / total * 100, 1)},
            'fertilizer': {'amount': agg['fertilizer'] or 0, 'percentage': round(float(agg['fertilizer'] or 0) / total * 100, 1)},
            'other': {'amount': agg['other'] or 0, 'percentage': round(float(agg['other'] or 0) / total * 100, 1)},
            'total': agg['total'] or 0,
        })

    @action(detail=False, methods=['get', 'post'], url_path='roi-calculator')
    def roi_calculator(self, request):
        """GET|POST /api/economic/roi-calculator/"""
        initial_investment = float(request.data.get('initial_investment', 0) or
                                   request.query_params.get('initial_investment', 0))
        period_months = int(request.data.get('period_months', 12) or
                            request.query_params.get('period_months', 12))

        if initial_investment <= 0:
            return Response({'detail': 'initial_investment > 0 olmalıdır.'}, status=status.HTTP_400_BAD_REQUEST)

        start = timezone.now().date() - timedelta(days=30 * period_months)
        agg = EconomicData.objects.filter(date__gte=start).aggregate(
            total_profit=Sum('net_profit')
        )
        total_profit = float(agg['total_profit'] or 0)
        roi = (total_profit / initial_investment) * 100
        payback_months = (initial_investment / (total_profit / period_months)) if total_profit > 0 else None

        return Response({
            'initial_investment': initial_investment,
            'period_months': period_months,
            'total_net_profit': round(total_profit, 2),
            'roi_percentage': round(roi, 2),
            'payback_months': round(payback_months, 1) if payback_months else None,
            'monthly_avg_profit': round(total_profit / period_months, 2),
        })

from rest_framework import serializers
from .models import EconomicData


class EconomicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicData
        fields = '__all__'
        read_only_fields = ('id', 'total_revenue', 'net_profit', 'roi_percentage', 'created_at', 'updated_at')


class EconomicSummarySerializer(serializers.Serializer):
    period = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_net_profit = serializers.DecimalField(max_digits=14, decimal_places=2)
    avg_roi = serializers.FloatField()
    revenue_gas = serializers.DecimalField(max_digits=14, decimal_places=2)
    revenue_fertilizer = serializers.DecimalField(max_digits=14, decimal_places=2)
    data_points = serializers.IntegerField()


class ROICalculatorSerializer(serializers.Serializer):
    initial_investment = serializers.FloatField()
    period_months = serializers.IntegerField(default=12)

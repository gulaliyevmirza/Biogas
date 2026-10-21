from rest_framework import serializers
from .models import ProductionLog, AIPrediction


class ProductionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionLog
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class AIPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPrediction
        fields = '__all__'
        read_only_fields = ('id',)


class LiveAnalyticsSerializer(serializers.Serializer):
    """Canlı panel üçün aggregated data"""
    timestamp = serializers.DateTimeField()
    methane_current = serializers.FloatField(allow_null=True)
    temperature_current = serializers.FloatField(allow_null=True)
    ph_current = serializers.FloatField(allow_null=True)
    biogas_today = serializers.FloatField()
    energy_today = serializers.FloatField()
    active_alerts = serializers.IntegerField()
    sensor_statuses = serializers.ListField()


class DailyReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    production = ProductionLogSerializer(allow_null=True)
    sensor_averages = serializers.DictField()
    alert_count = serializers.IntegerField()
    feedstock_received = serializers.FloatField()


class MonthlyReportSerializer(serializers.Serializer):
    month = serializers.CharField()
    total_methane = serializers.FloatField()
    total_biogas = serializers.FloatField()
    total_energy = serializers.FloatField()
    total_co2_reduction = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    avg_ph = serializers.FloatField()
    production_days = serializers.IntegerField()
    daily_breakdown = ProductionLogSerializer(many=True)

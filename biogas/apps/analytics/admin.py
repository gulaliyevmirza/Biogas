from django.contrib import admin
from .models import ProductionLog, AIPrediction


@admin.register(ProductionLog)
class ProductionLogAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'methane_output', 'biogas_output',
        'energy_generated', 'co2_reduction', 'temperature_avg', 'ph_avg'
    )
    search_fields = ('date',)
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = (
        'prediction_date', 'predicted_methane_24h',
        'predicted_methane_48h', 'predicted_methane_72h',
        'confidence_score', 'model_version', 'data_points_used'
    )
    readonly_fields = (
        'prediction_date', 'predicted_methane_24h', 'predicted_methane_48h',
        'predicted_methane_72h', 'confidence_score', 'recommendations',
        'model_version', 'data_points_used'
    )
    ordering = ('-prediction_date',)

    def has_add_permission(self, request):
        return False  # Yalnız Celery task vasitəsilə yaradılır

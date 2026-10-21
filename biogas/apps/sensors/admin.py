from django.contrib import admin
from .models import Sensor, SensorData


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'unit', 'location', 'threshold_min', 'threshold_max', 'is_active')
    list_filter = ('type', 'is_active', 'location')
    search_fields = ('name', 'location')
    list_editable = ('is_active',)
    ordering = ('name',)


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'value', 'timestamp', 'is_anomaly')
    list_filter = ('sensor__type', 'is_anomaly', 'sensor')
    search_fields = ('sensor__name',)
    readonly_fields = ('sensor', 'value', 'timestamp', 'is_anomaly')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False  # Sensor datası API vasitəsilə əlavə edilir

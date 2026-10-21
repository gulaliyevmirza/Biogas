from django.contrib import admin
from .models import EconomicData


@admin.register(EconomicData)
class EconomicDataAdmin(admin.ModelAdmin):
    list_display = (
        'date', 'revenue_gas', 'revenue_fertilizer',
        'total_revenue', 'expenses', 'net_profit', 'roi_percentage'
    )
    search_fields = ('date', 'notes')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('total_revenue', 'net_profit', 'roi_percentage', 'created_at', 'updated_at')

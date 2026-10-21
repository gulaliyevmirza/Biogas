from django.contrib import admin
from .models import ProcessOptimization


@admin.register(ProcessOptimization)
class ProcessOptimizationAdmin(admin.ModelAdmin):
    list_display = (
        'parameter_name', 'current_value', 'recommended_value',
        'unit', 'priority', 'applied', 'applied_at', 'applied_by'
    )
    list_filter = ('applied', 'priority')
    search_fields = ('parameter_name', 'reason')
    readonly_fields = ('created_at', 'applied_at', 'applied_by')
    ordering = ('-created_at',)
    actions = ['mark_as_applied']

    def mark_as_applied(self, request, queryset):
        from django.utils import timezone
        queryset.update(applied=True, applied_at=timezone.now(), applied_by=request.user)
    mark_as_applied.short_description = 'Seçilənləri tətbiq edilmiş kimi işarələ'

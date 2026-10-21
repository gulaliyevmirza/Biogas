from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('severity', 'sensor', 'message_short', 'is_read', 'email_sent', 'created_at')
    list_filter = ('severity', 'is_read', 'email_sent')
    search_fields = ('message', 'sensor__name')
    readonly_fields = ('created_at', 'read_at', 'email_sent')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    actions = ['mark_as_read']

    def message_short(self, obj):
        return obj.message[:80]
    message_short.short_description = 'Mesaj'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Seçilənləri oxunmuş kimi işarələ'

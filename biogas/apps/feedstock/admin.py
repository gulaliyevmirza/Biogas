from django.contrib import admin
from .models import Feedstock, Digestate


@admin.register(Feedstock)
class FeedstockAdmin(admin.ModelAdmin):
    list_display = ('type', 'quantity', 'received_date', 'status', 'supplier', 'moisture_content')
    list_filter = ('type', 'status')
    search_fields = ('supplier', 'notes')
    list_editable = ('status',)
    date_hierarchy = 'received_date'
    ordering = ('-received_date',)


@admin.register(Digestate)
class DigestateAdmin(admin.ModelAdmin):
    list_display = ('production_date', 'quantity', 'quality_grade', 'price_per_ton', 'sold', 'sold_date', 'buyer')
    list_filter = ('quality_grade', 'sold')
    search_fields = ('buyer',)
    list_editable = ('sold',)
    date_hierarchy = 'production_date'
    ordering = ('-production_date',)

from django.contrib import admin
from .models import DailyTrend

@admin.register(DailyTrend)
class DailyTrendAdmin(admin.ModelAdmin):
    list_display = ('date', 'suitable_items', 'unsuitable_items', 'created_at')
    list_filter = ('date',)
    search_fields = ('suitable_items', 'unsuitable_items')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('趋势信息', {
            'fields': ('date', 'suitable_items', 'unsuitable_items')
        }),
    )
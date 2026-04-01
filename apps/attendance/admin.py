from django.contrib import admin
from .models import AttendanceRecord, MakeupRecord

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_obj', 'date', 'status', 'consumed_lessons', 'created_by')
    list_filter = ('status', 'date', 'class_obj')
    search_fields = ('student__name', 'notes')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('student', 'class_obj', 'date', 'status')
        }),
        ('课时信息', {
            'fields': ('consumed_lessons', 'check_in_time')
        }),
        ('其他信息', {
            'fields': ('notes', 'created_by')
        }),
    )
    readonly_fields = ('created_at',)

@admin.register(MakeupRecord)
class MakeupRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'original_date', 'makeup_date', 'lessons_adjusted', 'approved_by')
    list_filter = ('original_date', 'makeup_date')
    search_fields = ('student__name', 'reason')
    date_hierarchy = 'created_at'
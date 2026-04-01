from django.contrib import admin
from .models import ClassSummary

@admin.register(ClassSummary)
class ClassSummaryAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'course', 'date', 'created_by', 'created_at')
    list_filter = ('class_obj', 'course', 'date')
    search_fields = ('content', 'homework', 'notes')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('class_obj', 'course', 'date')
        }),
        ('教学内容', {
            'fields': ('content', 'homework')
        }),
        ('学生表现', {
            'fields': ('outstanding_students', 'improvement_students')
        }),
        ('其他信息', {
            'fields': ('notes', 'created_by')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
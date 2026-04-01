from django.contrib import admin
from .models import Class

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'teacher', 'student_count', 'is_active', 'created_at')
    list_filter = ('level', 'is_active', 'created_at')
    search_fields = ('name', 'teacher__username')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'level', 'teacher', 'is_active')
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
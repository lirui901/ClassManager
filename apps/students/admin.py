from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'class_obj', 'remaining_lessons', 'is_active')
    list_filter = ('class_obj', 'gender', 'is_active')
    search_fields = ('name', 'phone', 'parent_phone')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'gender', 'birth_date', 'class_obj')
        }),
        ('联系方式', {
            'fields': ('phone', 'parent_phone', 'address')
        }),
        ('课时信息', {
            'fields': ('total_lessons', 'remaining_lessons')
        }),
        ('其他信息', {
            'fields': ('notes', 'is_active')
        }),
    )
    
    actions = ['add_10_lessons', 'reset_lessons']
    
    def add_10_lessons(self, request, queryset):
        for student in queryset:
            student.add_lessons(10)
        self.message_user(request, f'已为 {queryset.count()} 名学生增加10课时')
    add_10_lessons.short_description = '增加10课时'
    
    def reset_lessons(self, request, queryset):
        queryset.update(total_lessons=0, remaining_lessons=0)
        self.message_user(request, '已重置课时')
    reset_lessons.short_description = '重置课时'
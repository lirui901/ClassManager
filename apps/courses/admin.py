from django.contrib import admin
from .models import Course, Schedule

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration')
    search_fields = ('name',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'course', 'weekday', 'start_time', 'end_time', 'classroom')
    list_filter = ('weekday', 'is_active')
    search_fields = ('class_obj__name', 'course__name')
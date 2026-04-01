from django.apps import AppConfig

class StudentsConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.students'
    verbose_name = '学生管理'

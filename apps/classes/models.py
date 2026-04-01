from django.db import models
from django.conf import settings

class Class(models.Model):
    LEVEL_CHOICES = [
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
    ]
    
    name = models.CharField('班级名称', max_length=100)
    level = models.CharField('级别', max_length=20, choices=LEVEL_CHOICES, default='beginner')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='教师', 
        related_name='teaching_classes'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name='创建者', 
        related_name='created_classes'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"
    
    @property
    def student_count(self):
        return self.students.filter(is_active=True).count()
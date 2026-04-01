from django.db import models
from django.conf import settings
from apps.classes.models import Class
from apps.courses.models import Course

class ClassSummary(models.Model):
    """课堂总结"""
    class_obj = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        verbose_name='班级',
        related_name='summaries'
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        verbose_name='课程'
    )
    date = models.DateField('上课日期')
    
    # 教学内容
    content = models.TextField('教学内容')
    homework = models.TextField('课后作业', blank=True)
    
    # 学生表现
    outstanding_students = models.TextField('表现优秀学生', blank=True)
    improvement_students = models.TextField('需要改进学生', blank=True)
    
    # 备注
    notes = models.TextField('备注', blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '课堂总结'
        verbose_name_plural = '课堂总结'
        ordering = ['-date']
        unique_together = ['class_obj', 'date']
    
    def __str__(self):
        return f"{self.class_obj} - {self.date} 总结"
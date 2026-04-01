from django.db import models
from apps.classes.models import Class

class Course(models.Model):
    name = models.CharField('课程名称', max_length=100)
    description = models.TextField('课程描述', blank=True)
    duration = models.PositiveIntegerField('课时时长(分钟)', default=45)
    
    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'
    
    def __str__(self):
        return self.name

class Schedule(models.Model):
    WEEKDAY_CHOICES = [
        (1, '周一'), (2, '周二'), (3, '周三'), (4, '周四'),
        (5, '周五'), (6, '周六'), (7, '周日'),
    ]
    
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='班级', 
                                  related_name='schedules')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程')
    weekday = models.IntegerField('星期', choices=WEEKDAY_CHOICES)
    start_time = models.TimeField('开始时间')
    end_time = models.TimeField('结束时间')
    classroom = models.CharField('教室', max_length=50, blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '课程安排'
        verbose_name_plural = '课程安排'
        ordering = ['weekday', 'start_time']
    
    def __str__(self):
        return f"{self.class_obj} - {self.course} ({self.get_weekday_display()})"
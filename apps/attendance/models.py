from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.students.models import Student
from apps.classes.models import Class

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', '已签到'),
        ('absent', '缺勤'),
        ('leave', '请假'),
        ('late', '迟到'),
    ]
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        verbose_name='学生',
        related_name='attendance_records'
    )
    class_obj = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        verbose_name='班级'
    )
    date = models.DateField('签到日期', default=timezone.now)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='present')
    check_in_time = models.DateTimeField('签到时间', null=True, blank=True)
    consumed_lessons = models.PositiveIntegerField('消耗课时', default=1)
    notes = models.TextField('备注', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='记录人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '签到记录'
        verbose_name_plural = '签到记录'
        ordering = ['-date', '-created_at']
        unique_together = ['student', 'date', 'class_obj']
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # 如果是新签到且状态为已签到，消耗课时
        if not self.pk and self.status == 'present':
            self.student.consume_lesson(self.consumed_lessons)
        super().save(*args, **kwargs)

class MakeupRecord(models.Model):
    """补签记录（用于补签、退课时等）"""
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        verbose_name='学生',
        related_name='makeup_records'
    )
    original_date = models.DateField('原签到日期')
    makeup_date = models.DateField('补签日期')
    reason = models.TextField('补签原因')
    lessons_adjusted = models.IntegerField('调整课时', help_text='正数为增加课时，负数为扣除课时')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name='审批人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '补签记录'
        verbose_name_plural = '补签记录'
    
    def __str__(self):
        return f"{self.student} - {self.original_date} 补签"
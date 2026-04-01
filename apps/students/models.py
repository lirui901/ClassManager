from django.db import models
from django.conf import settings
from apps.classes.models import Class

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    
    # 关联用户账号
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        verbose_name='关联账号',
        related_name='student_profile'
    )
    
    name = models.CharField('姓名', max_length=50)
    gender = models.CharField('性别', max_length=1, choices=GENDER_CHOICES, default='M')
    birth_date = models.DateField('出生日期', null=True, blank=True)
    phone = models.CharField('联系电话', max_length=20, blank=True)
    parent_phone = models.CharField('家长电话', max_length=20, blank=True)
    address = models.TextField('家庭地址', blank=True)
    
    # 课时相关
    total_lessons = models.PositiveIntegerField('总课时', default=0)
    remaining_lessons = models.PositiveIntegerField('剩余课时', default=0)
    
    class_obj = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        verbose_name='所属班级', 
        related_name='students', 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    is_active = models.BooleanField('是否在读', default=True)
    notes = models.TextField('备注', blank=True)
    
    class Meta:
        verbose_name = '学生'
        verbose_name_plural = '学生'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.remaining_lessons}课时)"
    
    def consume_lesson(self, count=1):
        """消费课时"""
        if self.remaining_lessons >= count:
            self.remaining_lessons -= count
            self.save()
            return True
        return False
    
    def add_lessons(self, count):
        """增加课时"""
        self.total_lessons += count
        self.remaining_lessons += count
        self.save()
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('teacher', '老师'),
        ('student', '学生'),
        ('parent', '家长'),
    ]
    
    role = models.CharField('角色', max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField('手机号', max_length=20, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('个人简介', max_length=500, blank=True)
    
    # 学生专属字段
    student_id = models.CharField('学号', max_length=50, blank=True, unique=True, null=True)
    grade = models.CharField('年级', max_length=20, blank=True)
    parent_name = models.CharField('家长姓名', max_length=50, blank=True)
    parent_phone = models.CharField('家长电话', max_length=20, blank=True)
    
    # 老师专属字段
    teacher_id = models.CharField('工号', max_length=50, blank=True, unique=True, null=True)
    department = models.CharField('部门', max_length=50, blank=True)
    title = models.CharField('职称', max_length=50, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_teacher(self):
        return self.role == 'teacher'
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
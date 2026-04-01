from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .forms import LoginForm, RegisterForm
from apps.attendance.models import AttendanceRecord
from apps.summaries.models import ClassSummary
from apps.students.models import Student
from apps.courses.models import Schedule, Course
from datetime import timedelta
import calendar

# ==================== 认证相关视图 ====================

def login_view(request):
    """用户登录视图"""
    if request.user.is_authenticated:
        # 根据角色重定向到对应的仪表盘
        role = request.session.get('selected_role', request.user.role)
        if role == 'teacher' and (request.user.is_teacher or request.user.is_admin_user):
            return redirect('teacher_dashboard')
        elif role == 'student' and (request.user.is_student or request.user.is_admin_user):
            return redirect('student_dashboard')
        else:
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{username}！')
                
                # 登录后根据角色重定向
                if user.is_teacher:
                    return redirect('teacher_dashboard')
                elif user.is_student:
                    return redirect('student_dashboard')
                else:
                    return redirect('dashboard')
        messages.error(request, '用户名或密码错误')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    """用户注册视图"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'注册成功，欢迎{user.username}！')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def logout_view(request):
    """用户登出视图"""
    logout(request)
    messages.info(request, '您已成功退出登录')
    return redirect('login')

@login_required
def switch_role(request, role):
    """切换用户角色视图"""
    if role not in ['teacher', 'student', 'admin']:
        messages.error(request, '无效的角色')
        return redirect('dashboard')
    
    # 检查用户是否有权限切换到此角色
    if role == 'teacher' and not (request.user.is_teacher or request.user.is_admin_user):
        messages.error(request, '您没有权限切换到老师端')
        return redirect('dashboard')
    
    if role == 'student' and not (request.user.is_student or request.user.is_admin_user):
        messages.error(request, '您没有权限切换到学生端')
        return redirect('dashboard')
    
    # 保存角色到 session
    request.session['selected_role'] = role
    
    # 根据角色重定向
    if role == 'teacher':
        return redirect('teacher_dashboard')
    elif role == 'student':
        return redirect('student_dashboard')
    else:
        return redirect('dashboard')

# ==================== 管理端仪表盘 ====================

@login_required
def dashboard(request):
    """管理端首页仪表盘"""
    # 获取用户创建的班级
    classes = request.user.created_classes.all()
    
    # 统计信息
    class_count = classes.count()
    student_count = sum(c.student_count for c in classes)
    
    # 今日签到统计
    today = timezone.now().date()
    today_attendance = AttendanceRecord.objects.filter(
        class_obj__in=classes,
        date=today,
        status='present'
    ).count()
    
    # 最近签到记录
    recent_attendance = AttendanceRecord.objects.filter(
        class_obj__in=classes
    ).select_related('student', 'class_obj').order_by('-created_at')[:10]
    
    # 最近课堂总结
    recent_summaries = ClassSummary.objects.filter(
        class_obj__in=classes
    ).select_related('class_obj', 'course', 'created_by').order_by('-date')[:5]
    
    context = {
        'class_count': class_count,
        'student_count': student_count,
        'today_attendance': today_attendance,
        'recent_attendance': recent_attendance,
        'recent_summaries': recent_summaries,
        'current_role': request.session.get('selected_role', 'admin'),
    }
    return render(request, 'dashboard.html', context)

# ==================== 老师端视图 ====================

@login_required
def teacher_dashboard(request):
    """老师端首页"""
    if not request.user.is_teacher and not request.user.is_admin_user:
        messages.error(request, '您没有权限访问老师端')
        return redirect('dashboard')
    
    # 获取老师负责的班级
    classes = request.user.created_classes.all()
    
    # 统计信息
    class_count = classes.count()
    student_count = sum(c.student_count for c in classes)
    
    # 今日签到统计
    today = timezone.now().date()
    today_attendance = AttendanceRecord.objects.filter(
        class_obj__in=classes,
        date=today,
        status='present'
    ).count()
    
    # 待处理的补签申请
    from apps.attendance.models import MakeupRecord
    pending_makeup = MakeupRecord.objects.filter(
        student__class_obj__in=classes,
        approved_by__isnull=True
    ).count()
    
    context = {
        'class_count': class_count,
        'student_count': student_count,
        'today_attendance': today_attendance,
        'pending_makeup': pending_makeup,
        'classes': classes,
        'current_role': 'teacher',
    }
    return render(request, 'accounts/teacher_dashboard.html', context)

# ==================== 学生端视图 ====================

@login_required
def student_dashboard(request):
    """学生端首页"""
    if not request.user.is_student and not request.user.is_admin_user:
        messages.error(request, '您没有权限访问学生端')
        return redirect('dashboard')
    
    # 通过关联的用户查找学生记录
    try:
        student = request.user.student_profile
    except:
        student = None
    
    # 获取学生的签到记录
    recent_attendance = []
    month_attendance = 0
    attendance_rate = 0
    recent_summaries = []
    
    if student:
        recent_attendance = AttendanceRecord.objects.filter(
            student=student
        ).select_related('class_obj').order_by('-date')[:10]
        
        # 本月出勤统计
        today = timezone.now().date()
        first_day = today.replace(day=1)
        month_attendance = AttendanceRecord.objects.filter(
            student=student,
            date__gte=first_day,
            date__lte=today,
            status='present'
        ).count()
        
        total_days = (today - first_day).days + 1
        attendance_rate = (month_attendance / total_days * 100) if total_days > 0 else 0
        
        # 获取课堂总结
        if student.class_obj:
            recent_summaries = ClassSummary.objects.filter(
                class_obj=student.class_obj
            ).select_related('course', 'created_by').order_by('-date')[:5]
    
    context = {
        'student': student,
        'recent_attendance': recent_attendance,
        'month_attendance': month_attendance,
        'attendance_rate': round(attendance_rate, 1),
        'recent_summaries': recent_summaries,
        'current_role': 'student',
    }
    return render(request, 'accounts/student_dashboard.html', context)

@login_required
def student_courses(request):
    """学生端 - 我的课程"""
    if not request.user.is_student and not request.user.is_admin_user:
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    # 通过关联的用户查找学生记录
    try:
        student = request.user.student_profile
    except:
        student = None
    
    courses = []
    if student and student.class_obj:
        # 获取班级的课程安排
        schedules = Schedule.objects.filter(
            class_obj=student.class_obj,
            is_active=True
        ).select_related('course')
        
        for schedule in schedules:
            courses.append({
                'name': schedule.course.name,
                'description': schedule.course.description,
                'weekday': schedule.get_weekday_display(),
                'start_time': schedule.start_time,
                'end_time': schedule.end_time,
                'classroom': schedule.classroom,
                'duration': schedule.course.duration
            })
    
    context = {
        'student': student,
        'courses': courses,
        'current_role': 'student',
    }
    return render(request, 'accounts/student_courses.html', context)

@login_required
def student_attendance(request):
    """学生端 - 考勤记录"""
    if not request.user.is_student and not request.user.is_admin_user:
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    # 通过关联的用户查找学生记录
    try:
        student = request.user.student_profile
    except:
        student = None
    
    # 获取年份和月份参数
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = timezone.now().year
        month = timezone.now().month
    
    # 获取该月的第一天和最后一天
    first_day = timezone.datetime(year, month, 1).date()
    if month == 12:
        last_day = timezone.datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = timezone.datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # 获取该月的考勤记录
    attendance_records = []
    if student:
        records = AttendanceRecord.objects.filter(
            student=student,
            date__gte=first_day,
            date__lte=last_day
        ).order_by('-date')
        
        for record in records:
            attendance_records.append({
                'date': record.date,
                'status': record.status,
                'status_display': record.get_status_display(),
                'check_in_time': record.check_in_time,
                'consumed_lessons': record.consumed_lessons,
                'class_name': record.class_obj.name
            })
    
    # 统计信息
    total_days = (last_day - first_day).days + 1
    present_count = len([r for r in attendance_records if r['status'] == 'present'])
    late_count = len([r for r in attendance_records if r['status'] == 'late'])
    leave_count = len([r for r in attendance_records if r['status'] == 'leave'])
    absent_count = len([r for r in attendance_records if r['status'] == 'absent'])
    
    attendance_rate = (present_count / total_days * 100) if total_days > 0 else 0
    
    # 生成日历数据
    cal = calendar.monthcalendar(year, month)
    month_days = []
    for week in cal:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append(None)
            else:
                date = timezone.datetime(year, month, day).date()
                record = next((r for r in attendance_records if r['date'] == date), None)
                week_days.append({
                    'day': day,
                    'date': date,
                    'record': record
                })
        month_days.append(week_days)
    
    # 月份导航
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
        'present_count': present_count,
        'late_count': late_count,
        'leave_count': leave_count,
        'absent_count': absent_count,
        'attendance_rate': round(attendance_rate, 1),
        'year': year,
        'month': month,
        'month_name': f'{year}年{month}月',
        'month_days': month_days,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'current_role': 'student',
    }
    return render(request, 'accounts/student_attendance.html', context)

@login_required
def student_report(request):
    """学生端 - 学习报告"""
    if not request.user.is_student and not request.user.is_admin_user:
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    # 通过关联的用户查找学生记录
    try:
        student = request.user.student_profile
    except:
        student = None
    
    # 获取学期范围（最近3个月）
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=90)
    
    # 统计数据
    stats = {
        'total_lessons': 0,
        'remaining_lessons': 0,
        'attended_lessons': 0,
        'late_times': 0,
        'leave_times': 0,
        'absent_times': 0,
        'attendance_rate': 0,
        'total_hours': 0,
        'average_score': 85,
    }
    
    if student:
        stats['total_lessons'] = student.total_lessons
        stats['remaining_lessons'] = student.remaining_lessons
        
        # 获取近3个月的考勤统计
        records = AttendanceRecord.objects.filter(
            student=student,
            date__gte=start_date,
            date__lte=end_date
        )
        
        stats['attended_lessons'] = records.filter(status='present').count()
        stats['late_times'] = records.filter(status='late').count()
        stats['leave_times'] = records.filter(status='leave').count()
        stats['absent_times'] = records.filter(status='absent').count()
        
        total_days = (end_date - start_date).days + 1
        if total_days > 0:
            stats['attendance_rate'] = round((stats['attended_lessons'] / total_days * 100), 1)
        else:
            stats['attendance_rate'] = 0
        
        # 计算总学时（假设每节课45分钟）
        stats['total_hours'] = stats['attended_lessons'] * 0.75
    
    # 月度趋势数据
    monthly_data = []
    for i in range(3):
        month_date = end_date - timedelta(days=30 * i)
        month_start = month_date.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
        
        if student:
            month_records = AttendanceRecord.objects.filter(
                student=student,
                date__gte=month_start,
                date__lte=month_end,
                status='present'
            )
            count = month_records.count()
        else:
            count = 0
        
        monthly_data.append({
            'month': f'{month_start.month}月',
            'count': count
        })
    
    monthly_data.reverse()
    
    # 最近课堂总结
    recent_summaries = []
    if student and student.class_obj:
        recent_summaries = ClassSummary.objects.filter(
            class_obj=student.class_obj
        ).select_related('course', 'created_by').order_by('-date')[:5]
    
    context = {
        'student': student,
        'stats': stats,
        'monthly_data': monthly_data,
        'recent_summaries': recent_summaries,
        'current_role': 'student',
    }
    return render(request, 'accounts/student_report.html', context)
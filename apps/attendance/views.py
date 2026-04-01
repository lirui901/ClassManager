from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from datetime import datetime
from .models import AttendanceRecord, MakeupRecord
from apps.students.models import Student
from apps.classes.models import Class

@login_required
def attendance_list(request):
    """签到记录列表页面"""
    classes = request.user.created_classes.all()
    return render(request, 'attendance/list.html', {'classes': classes})

@login_required
@require_http_methods(["GET"])
def api_attendance_records(request, class_id, date=None):
    """API: 获取某班级某天的签到记录"""
    class_obj = get_object_or_404(Class, id=class_id, created_by=request.user)
    
    if date:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        target_date = timezone.now().date()
    
    # 获取班级所有学生
    students = class_obj.students.filter(is_active=True)
    
    # 获取当天的签到记录
    records = AttendanceRecord.objects.filter(
        class_obj=class_obj,
        date=target_date
    ).select_related('student')
    
    # 构建返回数据
    result = []
    for student in students:
        record = records.filter(student=student).first()
        result.append({
            'student_id': student.id,
            'student_name': student.name,
            'remaining_lessons': student.remaining_lessons,
            'attendance_id': record.id if record else None,
            'status': record.status if record else None,
            'check_in_time': record.check_in_time.strftime('%H:%M') if record and record.check_in_time else None,
        })
    
    return JsonResponse({
        'date': target_date.strftime('%Y-%m-%d'),
        'records': result
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_check_in(request):
    """API: 签到"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        class_id = data.get('class_id')
        status = data.get('status', 'present')
        
        if not student_id or not class_id:
            return JsonResponse({'error': '学生ID和班级ID不能为空'}, status=400)
        
        student = get_object_or_404(Student, id=student_id, class_obj__created_by=request.user)
        class_obj = get_object_or_404(Class, id=class_id, created_by=request.user)
        
        today = timezone.now().date()
        
        record, created = AttendanceRecord.objects.get_or_create(
            student=student,
            class_obj=class_obj,
            date=today,
            defaults={
                'status': status,
                'check_in_time': timezone.now() if status == 'present' else None,
                'created_by': request.user
            }
        )
        
        if not created:
            # 更新状态
            old_status = record.status
            record.status = status
            if status == 'present' and not record.check_in_time:
                record.check_in_time = timezone.now()
            
            # 如果从未签到改为已签到，消耗课时
            if old_status != 'present' and status == 'present':
                student.consume_lesson()
            # 如果从已签到改为其他状态，退还课时
            elif old_status == 'present' and status != 'present':
                student.add_lessons(1)
            
            record.save()
        
        return JsonResponse({
            'success': True,
            'remaining': student.remaining_lessons,
            'check_in_time': record.check_in_time.strftime('%H:%M') if record.check_in_time else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'签到失败: {str(e)}'}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_makeup(request):
    """API: 补签/退课时"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        original_date = data.get('original_date')
        reason = data.get('reason', '')
        lessons_adjusted = data.get('lessons_adjusted', 0)
        
        # 验证必要参数
        if not student_id:
            return JsonResponse({'error': '学生ID不能为空'}, status=400)
        
        if not original_date:
            return JsonResponse({'error': '原签到日期不能为空'}, status=400)
        
        # 验证日期格式
        try:
            parsed_date = datetime.strptime(original_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': '日期格式错误，应为 YYYY-MM-DD'}, status=400)
        
        # 获取学生
        try:
            student = get_object_or_404(Student, id=student_id, class_obj__created_by=request.user)
        except:
            return JsonResponse({'error': '学生不存在或无权限'}, status=404)
        
        # 创建补签记录
        makeup = MakeupRecord.objects.create(
            student=student,
            original_date=parsed_date,
            makeup_date=timezone.now().date(),
            reason=reason,
            lessons_adjusted=int(lessons_adjusted),
            approved_by=request.user
        )
        
        # 调整课时
        if lessons_adjusted > 0:
            student.add_lessons(lessons_adjusted)
        elif lessons_adjusted < 0:
            student.consume_lesson(abs(lessons_adjusted))
        
        return JsonResponse({
            'success': True,
            'remaining': student.remaining_lessons,
            'message': f'补签成功，调整课时: {lessons_adjusted}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'处理失败: {str(e)}'}, status=500)
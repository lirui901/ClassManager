from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from .models import ClassSummary
from apps.classes.models import Class
from apps.courses.models import Course

@login_required
def summary_list(request):
    """课堂总结列表页面"""
    classes = request.user.created_classes.all()
    return render(request, 'summaries/list.html', {'classes': classes})

@login_required
@require_http_methods(["GET"])
def api_summaries(request, class_id):
    """API: 获取班级的课堂总结列表"""
    class_obj = get_object_or_404(Class, id=class_id, created_by=request.user)
    summaries = class_obj.summaries.select_related('course', 'created_by').order_by('-date')
    
    result = []
    for summary in summaries:
        result.append({
            'id': summary.id,
            'date': summary.date.strftime('%Y-%m-%d'),
            'course_name': summary.course.name,
            'content_preview': summary.content[:50] + '...' if len(summary.content) > 50 else summary.content,
            'created_by': summary.created_by.username if summary.created_by else '未知',
            'created_at': summary.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse(result, safe=False)

@login_required
@require_http_methods(["GET"])
def api_summary_detail(request, summary_id):
    """API: 获取课堂总结详情"""
    summary = get_object_or_404(ClassSummary, id=summary_id, class_obj__created_by=request.user)
    
    return JsonResponse({
        'id': summary.id,
        'class_id': summary.class_obj.id,
        'class_name': summary.class_obj.name,
        'course_id': summary.course.id,
        'course_name': summary.course.name,
        'date': summary.date.strftime('%Y-%m-%d'),
        'content': summary.content,
        'homework': summary.homework,
        'outstanding_students': summary.outstanding_students,
        'improvement_students': summary.improvement_students,
        'notes': summary.notes,
        'created_by': summary.created_by.username if summary.created_by else '未知',
        'created_at': summary.created_at.strftime('%Y-%m-%d %H:%M'),
        'updated_at': summary.updated_at.strftime('%Y-%m-%d %H:%M')
    })

@login_required
@require_http_methods(["POST"])
def api_add_summary(request):
    """API: 添加课堂总结"""
    data = json.loads(request.body)
    class_id = data.get('class_id')
    course_id = data.get('course_id')
    date = data.get('date')
    
    class_obj = get_object_or_404(Class, id=class_id, created_by=request.user)
    course = get_object_or_404(Course, id=course_id)
    
    # 检查是否已存在
    if ClassSummary.objects.filter(class_obj=class_obj, date=date).exists():
        return JsonResponse({'error': '该日期已存在课堂总结'}, status=400)
    
    summary = ClassSummary.objects.create(
        class_obj=class_obj,
        course=course,
        date=date,
        content=data.get('content', ''),
        homework=data.get('homework', ''),
        outstanding_students=data.get('outstanding_students', ''),
        improvement_students=data.get('improvement_students', ''),
        notes=data.get('notes', ''),
        created_by=request.user
    )
    
    return JsonResponse({
        'id': summary.id,
        'message': '创建成功'
    })

@login_required
@require_http_methods(["PUT"])
def api_edit_summary(request, summary_id):
    """API: 编辑课堂总结"""
    summary = get_object_or_404(ClassSummary, id=summary_id, class_obj__created_by=request.user)
    data = json.loads(request.body)
    
    summary.content = data.get('content', summary.content)
    summary.homework = data.get('homework', summary.homework)
    summary.outstanding_students = data.get('outstanding_students', summary.outstanding_students)
    summary.improvement_students = data.get('improvement_students', summary.improvement_students)
    summary.notes = data.get('notes', summary.notes)
    summary.save()
    
    return JsonResponse({'message': '更新成功'})

@login_required
@require_http_methods(["DELETE"])
def api_delete_summary(request, summary_id):
    """API: 删除课堂总结"""
    summary = get_object_or_404(ClassSummary, id=summary_id, class_obj__created_by=request.user)
    summary.delete()
    return JsonResponse({'message': '删除成功'})
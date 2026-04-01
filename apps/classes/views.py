from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json
from .models import Class

@login_required
def class_list(request):
    """班级列表页面"""
    classes = request.user.created_classes.all()
    return render(request, 'classes/list.html', {'classes': classes})

@login_required
@require_http_methods(["GET"])
def api_classes(request):
    """API: 获取班级列表"""
    classes = request.user.created_classes.all().values('id', 'name', 'level', 'student_count')
    return JsonResponse(list(classes), safe=False)

@login_required
@require_http_methods(["POST"])
def api_add_class(request):
    """API: 添加班级"""
    data = json.loads(request.body)
    name = data.get('name')
    level = data.get('level', 'beginner')
    
    if not name:
        return JsonResponse({'error': '班级名称不能为空'}, status=400)
    
    cls = Class.objects.create(
        name=name,
        level=level,
        created_by=request.user
    )
    
    return JsonResponse({
        'id': cls.id,
        'name': cls.name,
        'level': cls.level,
        'student_count': 0
    })

@login_required
@require_http_methods(["PUT"])
def api_edit_class(request, class_id):
    """API: 编辑班级"""
    cls = get_object_or_404(Class, id=class_id, created_by=request.user)
    data = json.loads(request.body)
    
    cls.name = data.get('name', cls.name)
    cls.level = data.get('level', cls.level)
    cls.is_active = data.get('is_active', cls.is_active)
    cls.save()
    
    return JsonResponse({
        'id': cls.id,
        'name': cls.name,
        'level': cls.level,
        'is_active': cls.is_active
    })

@login_required
@require_http_methods(["DELETE"])
def api_delete_class(request, class_id):
    """API: 删除班级"""
    cls = get_object_or_404(Class, id=class_id, created_by=request.user)
    cls.delete()
    return JsonResponse({'message': '删除成功'})
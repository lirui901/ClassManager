from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
import json
from .models import Student
from apps.classes.models import Class
from apps.accounts.models import User

@login_required
def student_list(request):
    """学生列表页面"""
    classes = request.user.created_classes.all()
    return render(request, 'students/list.html', {'classes': classes})

@login_required
@require_http_methods(["GET"])
def api_students(request, class_id):
    """API: 获取班级学生列表"""
    class_obj = get_object_or_404(Class, id=class_id, created_by=request.user)
    students = class_obj.students.filter(is_active=True)
    
    result = []
    for student in students:
        result.append({
            'id': student.id,
            'name': student.name,
            'gender': student.gender,
            'phone': student.phone,
            'remaining_lessons': student.remaining_lessons,
            'has_account': student.user is not None,
            'username': student.user.username if student.user else None
        })
    
    return JsonResponse(result, safe=False)

@login_required
@require_http_methods(["GET"])
def api_student_detail(request, student_id):
    """API: 获取学生详情"""
    student = get_object_or_404(Student, id=student_id, class_obj__created_by=request.user)
    return JsonResponse({
        'id': student.id,
        'name': student.name,
        'gender': student.gender,
        'birth_date': student.birth_date,
        'phone': student.phone,
        'parent_phone': student.parent_phone,
        'address': student.address,
        'total_lessons': student.total_lessons,
        'remaining_lessons': student.remaining_lessons,
        'notes': student.notes,
        'has_account': student.user is not None,
        'username': student.user.username if student.user else None
    })

@login_required
@require_http_methods(["POST"])
def api_add_student(request):
    """API: 添加学生（可选择是否创建账号）"""
    data = json.loads(request.body)
    class_id = data.get('class_id')
    name = data.get('name')
    
    if not class_id or not name:
        return JsonResponse({'error': '班级ID和学生姓名不能为空'}, status=400)
    
    class_obj = get_object_or_404(Class, id=class_id, created_by=request.user)
    
    # 检查是否要创建账号
    create_account = data.get('create_account', False)
    username = data.get('username', '')
    password = data.get('password', '')
    
    user = None
    account_created = False
    
    if create_account:
        if not username:
            return JsonResponse({'error': '创建账号需要填写用户名'}, status=400)
        if not password:
            return JsonResponse({'error': '创建账号需要填写密码'}, status=400)
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '用户名已存在，请更换用户名'}, status=400)
        
        # 创建用户账号
        user = User.objects.create_user(
            username=username,
            password=password,
            role='student',
            student_id=username,
            first_name=name
        )
        account_created = True
    
    # 创建学生记录
    student = Student.objects.create(
        name=name,
        gender=data.get('gender', 'M'),
        birth_date=data.get('birth_date'),
        phone=data.get('phone', ''),
        parent_phone=data.get('parent_phone', ''),
        address=data.get('address', ''),
        total_lessons=data.get('total_lessons', 0),
        remaining_lessons=data.get('total_lessons', 0),
        class_obj=class_obj,
        notes=data.get('notes', ''),
        user=user
    )
    
    response_data = {
        'id': student.id,
        'name': student.name,
        'remaining_lessons': student.remaining_lessons,
        'account_created': account_created
    }
    
    if account_created:
        response_data['username'] = username
        response_data['password'] = password
    
    return JsonResponse(response_data)

@login_required
@require_http_methods(["PUT"])
def api_edit_student(request, student_id):
    """API: 编辑学生"""
    student = get_object_or_404(Student, id=student_id, class_obj__created_by=request.user)
    data = json.loads(request.body)
    
    student.name = data.get('name', student.name)
    student.gender = data.get('gender', student.gender)
    student.phone = data.get('phone', student.phone)
    student.parent_phone = data.get('parent_phone', student.parent_phone)
    student.address = data.get('address', student.address)
    student.notes = data.get('notes', student.notes)
    student.save()
    
    return JsonResponse({'message': '更新成功'})

@login_required
@require_http_methods(["DELETE"])
def api_delete_student(request, student_id):
    """API: 删除学生"""
    student = get_object_or_404(Student, id=student_id, class_obj__created_by=request.user)
    # 如果有关联的用户账号，可以选择是否删除
    if student.user:
        # 可以选择删除账号或只是解除关联
        pass
    student.delete()
    return JsonResponse({'message': '删除成功'})

@login_required
@require_http_methods(["POST"])
def api_add_lessons(request, student_id):
    """API: 增加课时"""
    student = get_object_or_404(Student, id=student_id, class_obj__created_by=request.user)
    data = json.loads(request.body)
    count = data.get('count', 0)
    
    if count > 0:
        student.add_lessons(count)
        return JsonResponse({
            'message': f'成功增加{count}课时',
            'remaining_lessons': student.remaining_lessons
        })
    
    return JsonResponse({'error': '课时数量必须大于0'}, status=400)

@login_required
@require_http_methods(["POST"])
def api_batch_create_accounts(request):
    """批量为学生创建账号"""
    data = json.loads(request.body)
    class_id = data.get('class_id')
    
    class_obj = get_object_or_404(Class, id=class_id, created_by=request.user)
    
    # 获取班级中没有账号的学生
    students = class_obj.students.filter(user__isnull=True, is_active=True)
    
    results = []
    for student in students:
        # 生成用户名：拼音或学号
        username = student.name
        password = '123456'  # 默认密码
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            username = f"{username}{student.id}"
        
        # 创建用户账号
        user = User.objects.create_user(
            username=username,
            password=password,
            role='student',
            student_id=username,
            first_name=student.name
        )
        
        student.user = user
        student.save()
        
        results.append({
            'name': student.name,
            'username': username,
            'password': password
        })
    
    return JsonResponse({
        'success': True,
        'count': len(results),
        'results': results
    })

@login_required
@require_http_methods(["POST"])
def api_create_single_account(request):
    """为单个学生创建账号"""
    data = json.loads(request.body)
    student_id = data.get('student_id')
    
    student = get_object_or_404(Student, id=student_id, class_obj__created_by=request.user)
    
    if student.user:
        return JsonResponse({'error': '该学生已有账号'}, status=400)
    
    username = student.name
    password = '123456'
    
    # 检查用户名是否已存在
    if User.objects.filter(username=username).exists():
        username = f"{username}{student.id}"
    
    user = User.objects.create_user(
        username=username,
        password=password,
        role='student',
        student_id=username,
        first_name=student.name
    )
    
    student.user = user
    student.save()
    
    return JsonResponse({
        'success': True,
        'username': username,
        'password': password
    })

@login_required
@require_http_methods(["POST"])
def api_reset_password(request):
    """重置学生密码"""
    data = json.loads(request.body)
    student_id = data.get('student_id')
    new_password = data.get('password', '123456')
    
    student = get_object_or_404(Student, id=student_id, class_obj__created_by=request.user)
    
    if not student.user:
        return JsonResponse({'error': '该学生没有关联账号'}, status=400)
    
    student.user.set_password(new_password)
    student.user.save()
    
    return JsonResponse({'success': True})
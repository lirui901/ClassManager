from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Course

@login_required
def api_course_list(request):
    """API: 获取课程列表"""
    courses = Course.objects.all().values('id', 'name')
    return JsonResponse(list(courses), safe=False)
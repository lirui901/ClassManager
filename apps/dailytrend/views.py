from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import DailyTrend
import json

@login_required
@require_http_methods(["GET"])
def get_today_trend(request):
    """获取今天的趋势（宜忌）"""
    trend = DailyTrend.get_today_trend()
    
    # 将逗号分隔的字符串转换为列表
    suitable_list = [item.strip() for item in trend.suitable_items.split(',') if item.strip()]
    unsuitable_list = [item.strip() for item in trend.unsuitable_items.split(',') if item.strip()]
    
    return JsonResponse({
        'date': trend.date.strftime('%Y-%m-%d'),
        'suitable': suitable_list,
        'unsuitable': unsuitable_list
    })

@login_required
@csrf_exempt  # 添加这一行来临时解决 CSRF 问题
@require_http_methods(["POST"])
def refresh_trend(request):
    """刷新今天的趋势（重新生成）"""
    try:
        today = timezone.now().date()
        trend, created = DailyTrend.objects.update_or_create(
            date=today,
            defaults={
                'suitable_items': DailyTrend.generate_random_suitable(),
                'unsuitable_items': DailyTrend.generate_random_unsuitable()
            }
        )
        
        suitable_list = [item.strip() for item in trend.suitable_items.split(',') if item.strip()]
        unsuitable_list = [item.strip() for item in trend.unsuitable_items.split(',') if item.strip()]
        
        return JsonResponse({
            'success': True,
            'date': trend.date.strftime('%Y-%m-%d'),
            'suitable': suitable_list,
            'unsuitable': unsuitable_list
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
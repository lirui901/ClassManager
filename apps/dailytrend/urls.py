from django.urls import path
from . import views

urlpatterns = [
    path('api/today/', views.get_today_trend, name='api_today_trend'),
    path('api/refresh/', views.refresh_trend, name='api_refresh_trend'),
]
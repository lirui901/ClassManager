from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('api/class/<int:class_id>/', views.api_attendance_records, name='api_attendance_records'),
    path('api/class/<int:class_id>/<str:date>/', views.api_attendance_records, name='api_attendance_records_date'),
    path('api/checkin/', views.api_check_in, name='api_check_in'),
    path('api/makeup/', views.api_makeup, name='api_makeup'),
]
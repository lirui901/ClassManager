from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/courses/', views.student_courses, name='student_courses'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/report/', views.student_report, name='student_report'),
    path('switch/<str:role>/', views.switch_role, name='switch_role'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('api/class/<int:class_id>/', views.api_students, name='api_students'),
    path('api/<int:student_id>/', views.api_student_detail, name='api_student_detail'),
    path('api/add/', views.api_add_student, name='api_add_student'),
    path('api/<int:student_id>/edit/', views.api_edit_student, name='api_edit_student'),
    path('api/<int:student_id>/delete/', views.api_delete_student, name='api_delete_student'),
    path('api/<int:student_id>/add-lessons/', views.api_add_lessons, name='api_add_lessons'),
    path('api/batch-create-accounts/', views.api_batch_create_accounts, name='api_batch_create_accounts'),
    path('api/create-single-account/', views.api_create_single_account, name='api_create_single_account'),
    path('api/reset-password/', views.api_reset_password, name='api_reset_password'),
]
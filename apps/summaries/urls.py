from django.urls import path
from . import views

urlpatterns = [
    path('', views.summary_list, name='summary_list'),
    path('api/class/<int:class_id>/', views.api_summaries, name='api_summaries'),
    path('api/<int:summary_id>/', views.api_summary_detail, name='api_summary_detail'),
    path('api/add/', views.api_add_summary, name='api_add_summary'),
    path('api/<int:summary_id>/edit/', views.api_edit_summary, name='api_edit_summary'),
    path('api/<int:summary_id>/delete/', views.api_delete_summary, name='api_delete_summary'),
]
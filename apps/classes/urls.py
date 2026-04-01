from django.urls import path
from . import views

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('api/list/', views.api_classes, name='api_classes'),
    path('api/add/', views.api_add_class, name='api_add_class'),
    path('api/<int:class_id>/edit/', views.api_edit_class, name='api_edit_class'),
    path('api/<int:class_id>/delete/', views.api_delete_class, name='api_delete_class'),
]
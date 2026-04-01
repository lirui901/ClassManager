from django.urls import path
from . import views

urlpatterns = [
    path('api/list/', views.api_course_list, name='api_course_list'),
]
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import dashboard, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('classes/', include('apps.classes.urls')),
    path('students/', include('apps.students.urls')),
    path('courses/', include('apps.courses.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('summaries/', include('apps.summaries.urls')),
    path('dailytrend/', include('apps.dailytrend.urls')),  # 添加这一行
    path('dashboard/', dashboard, name='dashboard'),
    path('', login_view, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
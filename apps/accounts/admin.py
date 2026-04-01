from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('额外信息', {
            'fields': ('phone', 'avatar', 'bio'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('额外信息', {
            'fields': ('phone', 'avatar', 'bio'),
        }),
    )
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'company', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'company')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Əlavə Məlumat', {
            'fields': ('role', 'phone', 'profile_picture', 'company')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Əlavə Məlumat', {
            'fields': ('role', 'phone', 'company', 'email')
        }),
    )

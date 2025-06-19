"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, UserPreferences


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model."""
    
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'module_type', 'target_band_score', 'current_level',
        'is_staff', 'is_active', 'date_joined'
    )
    list_filter = (
        'module_type', 'current_level', 'is_staff', 'is_active',
        'date_joined', 'target_band_score'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        (_('IELTS Information'), {
            'fields': (
                'target_band_score', 'current_level', 'test_date',
                'module_type', 'timezone', 'language_background'
            )
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('IELTS Information'), {
            'fields': (
                'target_band_score', 'current_level', 'test_date',
                'module_type', 'timezone', 'language_background'
            )
        }),
    )


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for UserPreferences model."""
    
    list_display = (
        'user', 'preferred_practice_time', 'difficulty_preference',
        'theme', 'auto_save_enabled', 'email_notifications'
    )
    list_filter = (
        'difficulty_preference', 'theme', 'auto_save_enabled',
        'email_notifications'
    )
    search_fields = ('user__username', 'user__email')
    ordering = ('user__username',)

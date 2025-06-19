"""
User models for the IELTS Writing Test platform.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import BaseModel


class CustomUser(AbstractUser):
    """
    Custom user model with IELTS-specific fields.
    """
    MODULE_CHOICES = [
        ('academic', 'Academic'),
        ('general', 'General Training'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    # IELTS-specific fields
    target_band_score = models.DecimalField(
        max_digits=2, 
        decimal_places=1,
        validators=[MinValueValidator(1.0), MaxValueValidator(9.0)],
        null=True,
        blank=True,
        help_text="Target IELTS band score (1.0-9.0)"
    )
    current_level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='beginner'
    )
    test_date = models.DateField(
        null=True,
        blank=True,
        help_text="Planned IELTS test date"
    )
    module_type = models.CharField(
        max_length=20,
        choices=MODULE_CHOICES,
        default='academic'
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC'
    )
    language_background = models.CharField(
        max_length=50,
        blank=True,
        help_text="Native language or language background"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_module_type_display()})"

    class Meta:
        db_table = 'accounts_customuser'


class UserPreferences(BaseModel):
    """
    User preferences and settings.
    """
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]
    
    FONT_SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('mixed', 'Mixed'),
    ]
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    
    # Practice preferences
    preferred_practice_time = models.PositiveIntegerField(
        default=60,
        help_text="Preferred practice session duration in minutes"
    )
    auto_save_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    difficulty_preference = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='mixed'
    )
    
    # Display preferences
    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='light'
    )
    font_size = models.CharField(
        max_length=10,
        choices=FONT_SIZE_CHOICES,
        default='medium'
    )

    def __str__(self):
        return f"Preferences for {self.user.username}"

    class Meta:
        db_table = 'accounts_userpreferences'

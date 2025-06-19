"""
Core models for the IELTS Writing Test platform.
"""

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TimeStampedModel(BaseModel):
    """
    Abstract model with timestamp fields.
    Extends BaseModel with additional timestamp functionality.
    """
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

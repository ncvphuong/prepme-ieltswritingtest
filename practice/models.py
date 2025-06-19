"""
Practice models for the IELTS Writing Test platform.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

from core.models import BaseModel

User = get_user_model()


class Topic(BaseModel):
    """
    Categorization of writing tasks by topic.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Topic category (e.g., education, technology, environment)"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'practice_topic'
        ordering = ['name']


class PracticeTask(BaseModel):
    """
    Individual writing tasks/questions.
    """
    MODULE_CHOICES = [
        ('academic', 'Academic'),
        ('general', 'General Training'),
    ]
    
    TASK_CHOICES = [
        (1, 'Task 1'),
        (2, 'Task 2'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    # Task identification
    task_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique task code (e.g., AC_T1_001, GT_T2_045)"
    )
    title = models.CharField(max_length=200)
    
    # Task classification
    module_type = models.CharField(max_length=20, choices=MODULE_CHOICES)
    task_number = models.IntegerField(choices=TASK_CHOICES)
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='intermediate'
    )
    
    # Task content
    instruction = models.TextField(
        help_text="Task instructions for the student"
    )
    prompt = models.TextField(
        help_text="The actual writing prompt or question"
    )
    additional_materials = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional materials like charts, graphs, diagrams (for Task 1)"
    )
    word_limit_min = models.PositiveIntegerField(default=150)
    word_limit_max = models.PositiveIntegerField(default=250)
    time_limit_minutes = models.PositiveIntegerField(default=20)
    
    # Relationships
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(9.0)]
    )

    def __str__(self):
        return f"{self.task_code}: {self.title}"

    class Meta:
        db_table = 'practice_practicetask'
        ordering = ['task_code']
        indexes = [
            models.Index(fields=['module_type', 'task_number']),
            models.Index(fields=['difficulty_level']),
            models.Index(fields=['is_active']),
        ]


class Submission(BaseModel):
    """
    User's writing submissions.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('assessed', 'Assessed'),
    ]
    
    # References
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    task = models.ForeignKey(
        PracticeTask,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    
    # Submission content
    content = models.TextField(
        help_text="The user's written response"
    )
    word_count = models.PositiveIntegerField(default=0)
    
    # Session information
    time_spent_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Actual time spent writing in seconds"
    )
    session_id = models.UUIDField(
        default=uuid.uuid4,
        help_text="For tracking multi-part sessions"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_practice_mode = models.BooleanField(
        default=True,
        help_text="Whether this is practice mode or test simulation"
    )
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.task_code} ({self.status})"

    class Meta:
        db_table = 'practice_submission'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['task']),
            models.Index(fields=['submitted_at']),
        ]

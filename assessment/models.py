"""
Assessment models for AI-powered IELTS scoring.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

from core.models import BaseModel
from practice.models import Submission

User = get_user_model()


class Assessment(BaseModel):
    """
    AI assessment results for a submission.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('retry', 'Retry Required'),
    ]
    
    # Link to submission
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='assessment'
    )
    
    # Assessment status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Overall band score (1.0-9.0)
    overall_band_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('9.0'))],
        null=True,
        blank=True
    )
    
    # Individual criterion scores (IELTS Writing Assessment Criteria)
    task_achievement_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('9.0'))],
        null=True,
        blank=True,
        help_text="Task Achievement (Task 1) / Task Response (Task 2)"
    )
    
    coherence_cohesion_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('9.0'))],
        null=True,
        blank=True,
        help_text="Coherence and Cohesion"
    )
    
    lexical_resource_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('9.0'))],
        null=True,
        blank=True,
        help_text="Lexical Resource"
    )
    
    grammar_accuracy_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('1.0')), MaxValueValidator(Decimal('9.0'))],
        null=True,
        blank=True,
        help_text="Grammatical Range and Accuracy"
    )
    
    # AI processing metadata
    ai_model_used = models.CharField(
        max_length=100,
        blank=True,
        help_text="Claude model version used for assessment"
    )
    
    processing_time_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time taken for AI processing"
    )
    
    ai_confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        null=True,
        blank=True,
        help_text="AI confidence in the assessment (0.00-1.00)"
    )
    
    # Error handling
    error_message = models.TextField(
        blank=True,
        help_text="Error details if assessment failed"
    )
    
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of assessment retry attempts"
    )
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Assessment for {self.submission.task.task_code} - {self.submission.user.username}"
    
    @property
    def is_completed(self):
        return self.status == 'completed' and self.overall_band_score is not None
    
    @property
    def criterion_scores(self):
        """Return all four criterion scores as a dictionary."""
        return {
            'task_achievement': self.task_achievement_score,
            'coherence_cohesion': self.coherence_cohesion_score,
            'lexical_resource': self.lexical_resource_score,
            'grammar_accuracy': self.grammar_accuracy_score,
        }
    
    def calculate_overall_score(self):
        """Calculate overall band score from individual criteria."""
        scores = [s for s in self.criterion_scores.values() if s is not None]
        if len(scores) == 4:
            # IELTS uses average of four criteria, rounded to nearest 0.5
            average = sum(scores) / 4
            # Round to nearest 0.5
            return round(average * 2) / 2
        return None
    
    class Meta:
        db_table = 'assessment_assessment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['overall_band_score']),
            models.Index(fields=['created_at']),
        ]


class Feedback(BaseModel):
    """
    Detailed feedback comments for specific aspects of the writing.
    """
    FEEDBACK_TYPE_CHOICES = [
        ('overall', 'Overall Feedback'),
        ('task_achievement', 'Task Achievement'),
        ('coherence_cohesion', 'Coherence and Cohesion'),
        ('lexical_resource', 'Lexical Resource'),
        ('grammar_accuracy', 'Grammatical Range and Accuracy'),
        ('inline', 'Inline Comment'),
        ('suggestion', 'Improvement Suggestion'),
    ]
    
    SEVERITY_CHOICES = [
        ('info', 'Information'),
        ('suggestion', 'Suggestion'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    # Link to assessment
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='feedback_items'
    )
    
    # Feedback classification
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='overall'
    )
    
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default='info'
    )
    
    # Feedback content
    title = models.CharField(
        max_length=200,
        help_text="Brief title for the feedback point"
    )
    
    content = models.TextField(
        help_text="Detailed feedback explanation"
    )
    
    # Inline feedback positioning (for text-specific comments)
    text_start_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Character position where comment applies (start)"
    )
    
    text_end_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Character position where comment applies (end)"
    )
    
    highlighted_text = models.TextField(
        blank=True,
        help_text="Specific text that this feedback refers to"
    )
    
    # Suggestions for improvement
    suggestion = models.TextField(
        blank=True,
        help_text="Specific suggestion for improvement"
    )
    
    # AI metadata
    ai_confidence = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('1.00'))],
        null=True,
        blank=True,
        help_text="AI confidence in this feedback (0.00-1.00)"
    )
    
    def __str__(self):
        return f"{self.get_feedback_type_display()}: {self.title}"
    
    class Meta:
        db_table = 'assessment_feedback'
        ordering = ['feedback_type', 'text_start_position', 'created_at']
        indexes = [
            models.Index(fields=['feedback_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['assessment', 'feedback_type']),
        ]


class AssessmentRequest(BaseModel):
    """
    Queue for tracking assessment requests and processing status.
    """
    REQUEST_STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Request details
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='assessment_requests'
    )
    
    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        default='queued'
    )
    
    priority = models.IntegerField(
        default=0,
        help_text="Higher numbers = higher priority"
    )
    
    # Processing metadata
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    error_details = models.TextField(
        blank=True,
        help_text="Error details if processing failed"
    )
    
    retry_after = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to retry if failed"
    )
    
    # Result reference
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests'
    )
    
    def __str__(self):
        return f"Assessment Request: {self.submission.task.task_code} - {self.status}"
    
    class Meta:
        db_table = 'assessment_request'
        ordering = ['-priority', 'created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['processing_started_at']),
        ]

"""
Assessment admin interface configuration.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Assessment, Feedback, AssessmentRequest


class FeedbackInline(admin.TabularInline):
    """Inline feedback items for assessments."""
    model = Feedback
    extra = 0
    readonly_fields = ('created_at', 'ai_confidence')
    fields = (
        'feedback_type', 'severity', 'title', 'content', 
        'suggestion', 'highlighted_text', 'ai_confidence'
    )


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Admin interface for Assessment model."""
    
    list_display = (
        'submission_link', 'status', 'overall_band_score', 
        'ai_model_used', 'processing_time_seconds', 'created_at'
    )
    
    list_filter = (
        'status', 'ai_model_used', 'overall_band_score', 
        'created_at', 'submission__task__module_type'
    )
    
    search_fields = (
        'submission__user__username', 'submission__task__task_code',
        'submission__task__title'
    )
    
    readonly_fields = (
        'submission_link', 'created_at', 'updated_at', 
        'processing_time_seconds', 'calculated_overall_score'
    )
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('submission_link', 'status', 'created_at', 'updated_at')
        }),
        ('Assessment Scores', {
            'fields': (
                'overall_band_score', 'calculated_overall_score',
                'task_achievement_score', 'coherence_cohesion_score',
                'lexical_resource_score', 'grammar_accuracy_score'
            )
        }),
        ('AI Processing', {
            'fields': (
                'ai_model_used', 'processing_time_seconds', 
                'ai_confidence_score', 'started_at', 'completed_at'
            )
        }),
        ('Error Handling', {
            'fields': ('error_message', 'retry_count'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [FeedbackInline]
    
    def submission_link(self, obj):
        """Link to the related submission."""
        url = reverse('admin:practice_submission_change', args=[obj.submission.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.submission))
    submission_link.short_description = 'Submission'
    
    def calculated_overall_score(self, obj):
        """Display calculated overall score."""
        calc_score = obj.calculate_overall_score()
        if calc_score:
            return f"{calc_score} (calculated)"
        return "N/A"
    calculated_overall_score.short_description = 'Calculated Overall Score'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin interface for Feedback model."""
    
    list_display = (
        'assessment_link', 'feedback_type', 'severity', 
        'title', 'ai_confidence', 'created_at'
    )
    
    list_filter = (
        'feedback_type', 'severity', 'assessment__status',
        'created_at', 'assessment__submission__task__module_type'
    )
    
    search_fields = (
        'title', 'content', 'assessment__submission__user__username',
        'assessment__submission__task__task_code'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Assessment Link', {
            'fields': ('assessment',)
        }),
        ('Feedback Details', {
            'fields': ('feedback_type', 'severity', 'title', 'content', 'suggestion')
        }),
        ('Text Positioning', {
            'fields': (
                'text_start_position', 'text_end_position', 'highlighted_text'
            ),
            'classes': ('collapse',)
        }),
        ('AI Metadata', {
            'fields': ('ai_confidence', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def assessment_link(self, obj):
        """Link to the related assessment."""
        url = reverse('admin:assessment_assessment_change', args=[obj.assessment.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.assessment))
    assessment_link.short_description = 'Assessment'


@admin.register(AssessmentRequest)
class AssessmentRequestAdmin(admin.ModelAdmin):
    """Admin interface for AssessmentRequest model."""
    
    list_display = (
        'submission_link', 'status', 'priority', 
        'processing_started_at', 'processing_completed_at', 'created_at'
    )
    
    list_filter = (
        'status', 'priority', 'created_at', 
        'processing_started_at', 'submission__task__module_type'
    )
    
    search_fields = (
        'submission__user__username', 'submission__task__task_code',
        'error_details'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Request Details', {
            'fields': ('submission', 'status', 'priority', 'created_at', 'updated_at')
        }),
        ('Processing Status', {
            'fields': (
                'processing_started_at', 'processing_completed_at',
                'retry_after', 'assessment'
            )
        }),
        ('Error Details', {
            'fields': ('error_details',),
            'classes': ('collapse',)
        })
    )
    
    def submission_link(self, obj):
        """Link to the related submission."""
        url = reverse('admin:practice_submission_change', args=[obj.submission.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.submission))
    submission_link.short_description = 'Submission'
    
    actions = ['retry_failed_assessments']
    
    def retry_failed_assessments(self, request, queryset):
        """Action to retry failed assessment requests."""
        failed_requests = queryset.filter(status='failed')
        count = failed_requests.update(status='queued', retry_after=None)
        self.message_user(
            request,
            f'Successfully queued {count} failed assessments for retry.'
        )
    retry_failed_assessments.short_description = 'Retry failed assessments'

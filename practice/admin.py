"""
Admin configuration for practice app.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Topic, PracticeTask, Submission


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin interface for Topic model."""
    
    list_display = ('name', 'category', 'is_active', 'task_count', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
    def task_count(self, obj):
        """Display the number of tasks in this topic."""
        return obj.tasks.count()
    task_count.short_description = 'Tasks'


@admin.register(PracticeTask)
class PracticeTaskAdmin(admin.ModelAdmin):
    """Admin interface for PracticeTask model."""
    
    list_display = (
        'task_code', 'title', 'module_type', 'task_number',
        'difficulty_level', 'topic', 'is_active', 'usage_count', 'average_score'
    )
    list_filter = (
        'module_type', 'task_number', 'difficulty_level', 'topic',
        'is_active', 'created_at'
    )
    search_fields = ('task_code', 'title', 'instruction', 'prompt')
    ordering = ('task_code',)
    readonly_fields = ('usage_count', 'average_score', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('task_code', 'title', 'topic')
        }),
        ('Classification', {
            'fields': ('module_type', 'task_number', 'difficulty_level')
        }),
        ('Content', {
            'fields': ('instruction', 'prompt', 'additional_materials')
        }),
        ('Settings', {
            'fields': (
                'word_limit_min', 'word_limit_max', 'time_limit_minutes', 'is_active'
            )
        }),
        ('Statistics', {
            'fields': ('usage_count', 'average_score'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Submission model."""
    
    list_display = (
        'user', 'task_code', 'status', 'word_count',
        'time_spent_display', 'is_practice_mode', 'submitted_at'
    )
    list_filter = (
        'status', 'is_practice_mode', 'task__module_type',
        'task__task_number', 'submitted_at', 'created_at'
    )
    search_fields = (
        'user__username', 'user__email', 'task__task_code',
        'task__title', 'content'
    )
    ordering = ('-created_at',)
    readonly_fields = (
        'session_id', 'started_at', 'created_at', 'updated_at', 'word_count'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'task', 'status', 'is_practice_mode')
        }),
        ('Content', {
            'fields': ('content', 'word_count')
        }),
        ('Session Information', {
            'fields': ('session_id', 'time_spent_seconds', 'started_at', 'submitted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def task_code(self, obj):
        """Display the task code."""
        return obj.task.task_code
    task_code.short_description = 'Task Code'
    task_code.admin_order_field = 'task__task_code'
    
    def time_spent_display(self, obj):
        """Display time spent in a human-readable format."""
        if obj.time_spent_seconds:
            minutes = obj.time_spent_seconds // 60
            seconds = obj.time_spent_seconds % 60
            return f"{minutes}m {seconds}s"
        return "-"
    time_spent_display.short_description = 'Time Spent'
    time_spent_display.admin_order_field = 'time_spent_seconds'

"""
Practice views for the IELTS Writing Test platform.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
import json

from .models import Topic, PracticeTask, Submission
from .forms import SubmissionForm


class PracticeListView(LoginRequiredMixin, ListView):
    """List view for practice tasks with filtering."""
    model = PracticeTask
    template_name = 'practice/list.html'
    context_object_name = 'tasks'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = PracticeTask.objects.filter(is_active=True).select_related('topic')
        
        # Filter by module type
        module_type = self.request.GET.get('module')
        if module_type:
            queryset = queryset.filter(module_type=module_type)
        
        # Filter by task number
        task_number = self.request.GET.get('task')
        if task_number:
            queryset = queryset.filter(task_number=task_number)
        
        # Filter by difficulty
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filter by topic
        topic = self.request.GET.get('topic')
        if topic:
            queryset = queryset.filter(topic_id=topic)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(prompt__icontains=search) |
                Q(instruction__icontains=search)
            )
        
        return queryset.order_by('task_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'topics': Topic.objects.filter(is_active=True),
            'module_types': PracticeTask.MODULE_CHOICES,
            'task_numbers': PracticeTask.TASK_CHOICES,
            'difficulties': PracticeTask.DIFFICULTY_CHOICES,
            'current_filters': {
                'module': self.request.GET.get('module', ''),
                'task': self.request.GET.get('task', ''),
                'difficulty': self.request.GET.get('difficulty', ''),
                'topic': self.request.GET.get('topic', ''),
                'search': self.request.GET.get('search', ''),
            }
        })
        return context


class PracticeTaskDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a specific practice task."""
    model = PracticeTask
    template_name = 'practice/task_detail.html'
    context_object_name = 'task'
    
    def get_queryset(self):
        return PracticeTask.objects.filter(is_active=True).select_related('topic')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if user has any drafts for this task
        user_drafts = Submission.objects.filter(
            user=self.request.user,
            task=self.object,
            status='draft'
        ).order_by('-created_at')
        
        context['has_draft'] = user_drafts.exists()
        context['latest_draft'] = user_drafts.first() if user_drafts.exists() else None
        
        return context


class StartPracticeView(LoginRequiredMixin, CreateView):
    """Start a new practice session."""
    model = Submission
    form_class = SubmissionForm
    template_name = 'practice/writing_interface.html'
    
    def get_task(self):
        return get_object_or_404(PracticeTask, pk=self.kwargs['task_id'], is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_task()
        
        # Check for existing draft
        existing_draft = Submission.objects.filter(
            user=self.request.user,
            task=task,
            status='draft'
        ).first()
        
        context.update({
            'task': task,
            'existing_draft': existing_draft,
            'word_limit_min': task.word_limit_min,
            'word_limit_max': task.word_limit_max,
            'time_limit': task.time_limit_minutes,
        })
        
        return context
    
    def form_valid(self, form):
        task = self.get_task()
        submission = form.save(commit=False)
        submission.user = self.request.user
        submission.task = task
        submission.save()
        
        messages.success(self.request, 'Your practice session has been saved!')
        return redirect('practice:submit', submission_id=submission.id)


class SubmitPracticeView(LoginRequiredMixin, DetailView):
    """Submit and review practice."""
    model = Submission
    template_name = 'practice/submit.html'
    context_object_name = 'submission'
    pk_url_kwarg = 'submission_id'
    
    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).select_related('task')
    
    def post(self, request, *args, **kwargs):
        submission = self.get_object()
        
        if submission.status == 'draft':
            submission.status = 'submitted'
            submission.submitted_at = timezone.now()
            submission.save()
            
            messages.success(request, 'Your submission has been completed! Assessment will be available soon.')
            return redirect('practice:history')
        
        return self.get(request, *args, **kwargs)


class PracticeHistoryView(LoginRequiredMixin, ListView):
    """User's practice history."""
    model = Submission
    template_name = 'practice/history.html'
    context_object_name = 'submissions'
    paginate_by = 10
    
    def get_queryset(self):
        return Submission.objects.filter(
            user=self.request.user
        ).select_related('task', 'task__topic').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submissions = self.get_queryset()
        
        context.update({
            'total_submissions': submissions.count(),
            'draft_count': submissions.filter(status='draft').count(),
            'submitted_count': submissions.filter(status='submitted').count(),
            'assessed_count': submissions.filter(status='assessed').count(),
        })
        
        return context


# AJAX views for auto-save functionality
def autosave_submission(request):
    """Auto-save submission content via AJAX."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        submission_id = request.POST.get('submission_id')
        content = request.POST.get('content', '')
        word_count = len(content.strip().split()) if content.strip() else 0
        
        try:
            submission = Submission.objects.get(
                id=submission_id,
                user=request.user,
                status='draft'
            )
            submission.content = content
            submission.word_count = word_count
            submission.save()
            
            return JsonResponse({
                'success': True,
                'word_count': word_count,
                'message': 'Draft saved'
            })
        except Submission.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Submission not found'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

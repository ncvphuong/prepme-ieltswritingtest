"""
Authentication and user account views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy

from .models import CustomUser, UserPreferences


class CustomLoginView(LoginView):
    """Custom login view with enhanced functionality."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


class RegisterView(CreateView):
    """User registration view."""
    model = CustomUser
    template_name = 'accounts/register.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'password']
    success_url = reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        # Create user preferences
        UserPreferences.objects.create(user=user)
        
        # Log the user in
        login(self.request, user)
        messages.success(self.request, f'Welcome to IELTS Writing Pro, {user.first_name or user.username}!')
        
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    """User dashboard view."""
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add dashboard statistics
        context.update({
            'total_submissions': user.submissions.count(),
            'completed_assessments': user.submissions.filter(status='assessed').count(),
            'target_band_score': user.target_band_score or 'Not set',
            'current_level': user.get_current_level_display(),
            'module_type': user.get_module_type_display(),
        })
        
        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    """User profile management view."""
    model = CustomUser
    template_name = 'accounts/profile.html'
    fields = [
        'first_name', 'last_name', 'email', 'target_band_score',
        'current_level', 'test_date', 'module_type', 'language_background'
    ]
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)


class PreferencesView(LoginRequiredMixin, UpdateView):
    """User preferences management view."""
    model = UserPreferences
    template_name = 'accounts/preferences.html'
    fields = [
        'preferred_practice_time', 'auto_save_enabled', 'email_notifications',
        'difficulty_preference', 'theme', 'font_size'
    ]
    success_url = reverse_lazy('accounts:preferences')
    
    def get_object(self):
        preferences, created = UserPreferences.objects.get_or_create(user=self.request.user)
        return preferences
    
    def form_valid(self, form):
        messages.success(self.request, 'Your preferences have been updated successfully!')
        return super().form_valid(form)

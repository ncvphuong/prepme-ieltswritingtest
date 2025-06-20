"""
Progress views - placeholder implementations.
"""
from django.views.generic import TemplateView


class ProgressDashboardView(TemplateView):
    template_name = 'progress/dashboard.html'


class AnalyticsView(TemplateView):
    template_name = 'progress/analytics.html'


class GoalsView(TemplateView):
    template_name = 'progress/goals.html'

"""
Practice views - placeholder implementations.
"""
from django.views.generic import TemplateView


class PracticeListView(TemplateView):
    template_name = 'practice/list.html'


class PracticeTaskDetailView(TemplateView):
    template_name = 'practice/task_detail.html'


class StartPracticeView(TemplateView):
    template_name = 'practice/start.html'


class SubmitPracticeView(TemplateView):
    template_name = 'practice/submit.html'


class PracticeHistoryView(TemplateView):
    template_name = 'practice/history.html'

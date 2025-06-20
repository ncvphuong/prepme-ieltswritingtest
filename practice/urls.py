"""
URL configuration for practice app.
"""
from django.urls import path
from . import views

app_name = 'practice'

urlpatterns = [
    path('', views.PracticeListView.as_view(), name='list'),
    path('task/<int:pk>/', views.PracticeTaskDetailView.as_view(), name='task_detail'),
    path('start/<int:task_id>/', views.StartPracticeView.as_view(), name='start'),
    path('submit/<int:submission_id>/', views.SubmitPracticeView.as_view(), name='submit'),
    path('history/', views.PracticeHistoryView.as_view(), name='history'),
    path('autosave/', views.autosave_submission, name='autosave'),
]
"""
URL configuration for progress app.
"""
from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('', views.ProgressDashboardView.as_view(), name='dashboard'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('goals/', views.GoalsView.as_view(), name='goals'),
]
"""
URL configuration for assessment app.
"""

from django.urls import path
from . import views

app_name = 'assessment'

urlpatterns = [
    # Assessment detail view
    path('submission/<int:submission_id>/', views.AssessmentDetailView.as_view(), name='detail'),
    
    # Assessment history
    path('history/', views.UserAssessmentHistoryView.as_view(), name='history'),
    
    # AJAX endpoints
    path('request/<int:submission_id>/', views.request_assessment, name='request'),
    path('status/<int:submission_id>/', views.assessment_status, name='status'),
]
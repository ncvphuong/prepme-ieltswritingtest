"""
URL configuration for assessment app.
"""

from django.urls import path
from . import views, streaming_views

app_name = 'assessment'

urlpatterns = [
    # Assessment detail view
    path('submission/<int:submission_id>/', views.AssessmentDetailView.as_view(), name='detail'),
    
    # Assessment history
    path('history/', views.UserAssessmentHistoryView.as_view(), name='history'),
    
    # Streaming assessment
    path('streaming/<int:submission_id>/', streaming_views.StreamingAssessmentView.as_view(), name='streaming'),
    path('stream/<int:submission_id>/', streaming_views.stream_assessment, name='stream'),
    path('quick/<int:submission_id>/', streaming_views.quick_assess, name='quick'),
    
    # AJAX endpoints
    path('request/<int:submission_id>/', views.request_assessment, name='request'),
    path('status/<int:submission_id>/', views.assessment_status, name='status'),
]
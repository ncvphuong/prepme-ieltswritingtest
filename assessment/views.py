"""
Assessment views for displaying AI feedback and results.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone

from practice.models import Submission
from .models import Assessment, Feedback, AssessmentRequest
from .services import assessment_service


class AssessmentDetailView(LoginRequiredMixin, DetailView):
    """Display detailed assessment results for a submission."""
    model = Assessment
    template_name = 'assessment/detail.html'
    context_object_name = 'assessment'
    
    def get_object(self):
        """Get assessment by submission ID, ensuring user owns it."""
        submission_id = self.kwargs['submission_id']
        submission = get_object_or_404(
            Submission,
            id=submission_id,
            user=self.request.user
        )
        
        try:
            return Assessment.objects.get(submission=submission)
        except Assessment.DoesNotExist:
            # Create assessment request if none exists
            assessment_service.create_assessment_request(submission)
            messages.info(
                self.request,
                'Assessment has been requested and will be available shortly.'
            )
            return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.object:
            # Group feedback by type
            feedback_by_type = {}
            for feedback in self.object.feedback_items.all():
                if feedback.feedback_type not in feedback_by_type:
                    feedback_by_type[feedback.feedback_type] = []
                feedback_by_type[feedback.feedback_type].append(feedback)
            
            context['feedback_by_type'] = feedback_by_type
            context['submission'] = self.object.submission
            
            # Calculate score insights
            context['score_insights'] = self._get_score_insights(self.object)
        else:
            # No assessment yet, get submission
            submission_id = self.kwargs['submission_id']
            context['submission'] = get_object_or_404(
                Submission,
                id=submission_id,
                user=self.request.user
            )
        
        return context
    
    def _get_score_insights(self, assessment):
        """Generate insights about the scores."""
        insights = {
            'strengths': [],
            'weaknesses': [],
            'band_description': self._get_band_description(assessment.overall_band_score)
        }
        
        scores = assessment.criterion_scores
        avg_score = sum(s for s in scores.values() if s) / 4
        
        for criterion, score in scores.items():
            if score and score >= avg_score + 0.5:
                insights['strengths'].append({
                    'criterion': criterion.replace('_', ' ').title(),
                    'score': score
                })
            elif score and score <= avg_score - 0.5:
                insights['weaknesses'].append({
                    'criterion': criterion.replace('_', ' ').title(),
                    'score': score
                })
        
        return insights
    
    def _get_band_description(self, score):
        """Get IELTS band score description."""
        if not score:
            return "Not assessed"
        
        if score >= 9.0:
            return "Expert User"
        elif score >= 8.0:
            return "Very Good User"
        elif score >= 7.0:
            return "Good User"
        elif score >= 6.0:
            return "Competent User"
        elif score >= 5.0:
            return "Modest User"
        elif score >= 4.0:
            return "Limited User"
        elif score >= 3.0:
            return "Extremely Limited User"
        elif score >= 2.0:
            return "Intermittent User"
        else:
            return "Non-User"


class UserAssessmentHistoryView(LoginRequiredMixin, ListView):
    """Display user's assessment history."""
    model = Assessment
    template_name = 'assessment/history.html'
    context_object_name = 'assessments'
    paginate_by = 10
    
    def get_queryset(self):
        return Assessment.objects.filter(
            submission__user=self.request.user,
            status='completed'
        ).select_related(
            'submission', 'submission__task'
        ).order_by('-completed_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate statistics
        assessments = self.get_queryset()
        if assessments:
            context['avg_score'] = sum(
                a.overall_band_score for a in assessments if a.overall_band_score
            ) / len(assessments)
            
            context['best_score'] = max(
                (a.overall_band_score for a in assessments if a.overall_band_score),
                default=0
            )
            
            context['total_assessments'] = assessments.count()
        
        return context


def request_assessment(request, submission_id):
    """AJAX endpoint to request assessment for a submission."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        submission = get_object_or_404(
            Submission,
            id=submission_id,
            user=request.user,
            status='submitted'
        )
        
        # Check if assessment already exists
        existing_assessment = Assessment.objects.filter(
            submission=submission
        ).first()
        
        if existing_assessment:
            if existing_assessment.status == 'completed':
                return JsonResponse({
                    'status': 'completed',
                    'message': 'Assessment already completed',
                    'redirect_url': f'/assessment/{submission_id}/'
                })
            else:
                return JsonResponse({
                    'status': 'processing',
                    'message': 'Assessment is already in progress'
                })
        
        # Create assessment request
        assessment_request = assessment_service.create_assessment_request(submission)
        
        return JsonResponse({
            'status': 'requested',
            'message': 'Assessment has been requested and will be processed shortly',
            'request_id': assessment_request.id
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


def assessment_status(request, submission_id):
    """AJAX endpoint to check assessment status."""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)
    
    try:
        submission = get_object_or_404(
            Submission,
            id=submission_id,
            user=request.user
        )
        
        # Check for existing assessment
        assessment = Assessment.objects.filter(submission=submission).first()
        
        if assessment:
            return JsonResponse({
                'status': assessment.status,
                'overall_score': float(assessment.overall_band_score) if assessment.overall_band_score else None,
                'completed_at': assessment.completed_at.isoformat() if assessment.completed_at else None,
                'processing_time': assessment.processing_time_seconds,
                'view_url': f'/assessment/{submission_id}/' if assessment.status == 'completed' else None
            })
        
        # Check for assessment request
        request_obj = AssessmentRequest.objects.filter(submission=submission).first()
        
        if request_obj:
            return JsonResponse({
                'status': f'request_{request_obj.status}',
                'created_at': request_obj.created_at.isoformat(),
                'processing_started_at': request_obj.processing_started_at.isoformat() if request_obj.processing_started_at else None
            })
        
        return JsonResponse({
            'status': 'not_requested'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

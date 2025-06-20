"""
Streaming assessment views for real-time Claude feedback.
"""

import json
import time
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from practice.models import Submission
from .services import assessment_service
from .models import Assessment, AssessmentRequest


class StreamingAssessmentView(LoginRequiredMixin, TemplateView):
    """View for real-time streaming assessment."""
    template_name = 'assessment/streaming.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission_id = self.kwargs['submission_id']
        
        submission = get_object_or_404(
            Submission,
            id=submission_id,
            user=self.request.user,
            status='submitted'
        )
        
        context['submission'] = submission
        return context


@login_required
def stream_assessment(request, submission_id):
    """Stream Claude assessment in real-time."""
    
    def generate_assessment_stream():
        try:
            submission = get_object_or_404(
                Submission,
                id=submission_id,
                user=request.user,
                status='submitted'
            )
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Starting AI assessment...'})}\n\n"
            time.sleep(1)
            
            # Check if assessment already exists
            existing_assessment = Assessment.objects.filter(submission=submission).first()
            if existing_assessment and existing_assessment.status == 'completed':
                yield f"data: {json.dumps({'type': 'complete', 'assessment_id': existing_assessment.id, 'redirect': f'/assessment/submission/{submission_id}/'})}\n\n"
                return
            
            # Create assessment request if needed
            yield f"data: {json.dumps({'type': 'status', 'message': 'Connecting to Claude AI...'})}\n\n"
            time.sleep(1)
            
            # Start assessment process
            yield f"data: {json.dumps({'type': 'status', 'message': 'Claude is analyzing your writing...'})}\n\n"
            
            # Simulate progress updates (in real implementation, you'd hook into the actual assessment)
            progress_messages = [
                'Analyzing task achievement...',
                'Evaluating coherence and cohesion...',
                'Checking lexical resource...',
                'Assessing grammatical accuracy...',
                'Generating detailed feedback...',
                'Finalizing assessment...'
            ]
            
            for i, message in enumerate(progress_messages):
                yield f"data: {json.dumps({'type': 'progress', 'message': message, 'percentage': (i + 1) * 15})}\n\n"
                time.sleep(2)  # Simulate processing time
            
            # Process the actual assessment
            assessment = assessment_service.assess_submission(submission)
            
            # Send completion with scores
            yield f"data: {json.dumps({
                'type': 'scores',
                'overall_score': float(assessment.overall_band_score),
                'task_achievement': float(assessment.task_achievement_score),
                'coherence_cohesion': float(assessment.coherence_cohesion_score),
                'lexical_resource': float(assessment.lexical_resource_score),
                'grammar_accuracy': float(assessment.grammar_accuracy_score)
            })}\n\n"
            
            time.sleep(1)
            
            # Send final completion
            yield f"data: {json.dumps({
                'type': 'complete',
                'message': 'Assessment completed successfully!',
                'assessment_id': assessment.id,
                'redirect': f'/assessment/submission/{submission_id}/'
            })}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    response = StreamingHttpResponse(
        generate_assessment_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response


@login_required 
def quick_assess(request, submission_id):
    """Quick non-streaming assessment endpoint."""
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
        existing_assessment = Assessment.objects.filter(submission=submission).first()
        if existing_assessment and existing_assessment.status == 'completed':
            return JsonResponse({
                'status': 'already_completed',
                'assessment_id': existing_assessment.id,
                'redirect_url': f'/assessment/submission/{submission_id}/'
            })
        
        # Process assessment
        assessment = assessment_service.assess_submission(submission)
        
        return JsonResponse({
            'status': 'completed',
            'assessment_id': assessment.id,
            'overall_score': float(assessment.overall_band_score),
            'processing_time': assessment.processing_time_seconds,
            'redirect_url': f'/assessment/submission/{submission_id}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
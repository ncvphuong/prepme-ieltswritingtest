"""
Claude SDK integration for IELTS writing assessment.
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.db import transaction

import anthropic

from .models import Assessment, Feedback, AssessmentRequest
from practice.models import Submission

logger = logging.getLogger(__name__)


class IELTSAssessmentService:
    """
    Service for AI-powered IELTS writing assessment using Claude.
    """
    
    def __init__(self):
        """Initialize the Claude client."""
        self.client = anthropic.Anthropic(
            api_key=getattr(settings, 'ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY'))
        )
        self.model = getattr(settings, 'CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        self.max_tokens = getattr(settings, 'CLAUDE_MAX_TOKENS', 4000)
    
    def assess_submission(self, submission: Submission) -> Assessment:
        """
        Assess a writing submission and return the assessment result.
        
        Args:
            submission: The submission to assess
            
        Returns:
            Assessment object with scores and feedback
            
        Raises:
            Exception: If assessment fails
        """
        start_time = time.time()
        
        try:
            # Create or get existing assessment
            assessment, created = Assessment.objects.get_or_create(
                submission=submission,
                defaults={
                    'status': 'processing',
                    'started_at': timezone.now(),
                    'ai_model_used': self.model
                }
            )
            
            if not created and assessment.status == 'completed':
                logger.info(f"Assessment already completed for submission {submission.id}")
                return assessment
            
            # Update status to processing
            assessment.status = 'processing'
            assessment.started_at = timezone.now()
            assessment.save()
            
            # Generate assessment prompt
            prompt = self._generate_assessment_prompt(submission)
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for more consistent scoring
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse the response
            assessment_data = self._parse_claude_response(response.content[0].text)
            
            # Update assessment with results
            processing_time = int(time.time() - start_time)
            
            with transaction.atomic():
                # Update assessment scores
                assessment.overall_band_score = assessment_data['overall_score']
                assessment.task_achievement_score = assessment_data['task_achievement']
                assessment.coherence_cohesion_score = assessment_data['coherence_cohesion']
                assessment.lexical_resource_score = assessment_data['lexical_resource']
                assessment.grammar_accuracy_score = assessment_data['grammar_accuracy']
                assessment.ai_confidence_score = assessment_data.get('confidence', 0.85)
                assessment.processing_time_seconds = processing_time
                assessment.status = 'completed'
                assessment.completed_at = timezone.now()
                assessment.save()
                
                # Create feedback items
                self._create_feedback_items(assessment, assessment_data['feedback'])
                
                # Update submission status
                submission.status = 'assessed'
                submission.save()
            
            logger.info(f"Assessment completed for submission {submission.id} in {processing_time}s")
            return assessment
            
        except Exception as e:
            logger.error(f"Assessment failed for submission {submission.id}: {str(e)}")
            
            # Update assessment with error
            if 'assessment' in locals():
                assessment.status = 'failed'
                assessment.error_message = str(e)
                assessment.retry_count += 1
                assessment.save()
            
            raise e
    
    def _generate_assessment_prompt(self, submission: Submission) -> str:
        """Generate the prompt for Claude to assess the writing."""
        
        task = submission.task
        task_type = "Task 1" if task.task_number == 1 else "Task 2"
        module_type = task.get_module_type_display()
        
        # Determine specific task criteria
        if task.task_number == 1:
            if task.module_type == 'academic':
                task_criterion = "Task Achievement"
                task_description = "How well the response addresses the task requirements, presents key features, and makes appropriate comparisons"
            else:  # general training
                task_criterion = "Task Achievement"
                task_description = "How well the response addresses the task requirements, covers all bullet points, and uses appropriate tone and format"
        else:  # Task 2
            task_criterion = "Task Response"
            task_description = "How well the response addresses the task, presents a clear position, and develops arguments with relevant examples"
        
        prompt = f"""You are an expert IELTS examiner with extensive experience in assessing {module_type} Writing {task_type}. You will assess this writing response according to the official IELTS Writing assessment criteria.

TASK INFORMATION:
- Module: {module_type}
- Task: {task_type}
- Task Code: {task.task_code}
- Title: {task.title}
- Word Limit: {task.word_limit_min}-{task.word_limit_max} words
- Actual Word Count: {submission.word_count} words

TASK PROMPT:
{task.prompt}

{f"TASK INSTRUCTIONS: {task.instruction}" if task.instruction else ""}

STUDENT RESPONSE:
{submission.content}

ASSESSMENT CRITERIA:
Please assess this response according to the four IELTS Writing criteria:

1. {task_criterion} (25%): {task_description}
2. Coherence and Cohesion (25%): Logical organization, clear progression, appropriate linking devices, paragraphing
3. Lexical Resource (25%): Range and accuracy of vocabulary, appropriate word choice, spelling accuracy
4. Grammatical Range and Accuracy (25%): Range of grammatical structures, accuracy, punctuation

SCORING SCALE:
Use the IELTS 9-band scale (1.0-9.0, in 0.5 increments):
- 9.0: Expert user
- 8.0-8.5: Very good user
- 7.0-7.5: Good user
- 6.0-6.5: Competent user
- 5.0-5.5: Modest user
- 4.0-4.5: Limited user
- 3.0-3.5: Extremely limited user
- 2.0-2.5: Intermittent user
- 1.0-1.5: Non-user

SPECIAL CONSIDERATIONS:
- Word count: {"Under minimum" if submission.word_count < task.word_limit_min else "Over maximum" if submission.word_count > task.word_limit_max else "Within range"}
- Penalties apply for significant under/over length
- Task type specific requirements must be met

REQUIRED OUTPUT FORMAT:
Please provide your assessment in the following JSON format:

{{
    "overall_score": X.X,
    "task_achievement": X.X,
    "coherence_cohesion": X.X,
    "lexical_resource": X.X,
    "grammar_accuracy": X.X,
    "confidence": 0.XX,
    "feedback": [
        {{
            "type": "overall",
            "title": "Overall Assessment",
            "content": "Comprehensive overview of the response quality and band score justification",
            "severity": "info"
        }},
        {{
            "type": "task_achievement",
            "title": "{task_criterion}",
            "content": "Detailed analysis of how well the task requirements were met",
            "severity": "info"
        }},
        {{
            "type": "coherence_cohesion",
            "title": "Coherence and Cohesion",
            "content": "Analysis of organization, flow, and linking",
            "severity": "info"
        }},
        {{
            "type": "lexical_resource",
            "title": "Lexical Resource",
            "content": "Assessment of vocabulary range, accuracy, and appropriateness",
            "severity": "info"
        }},
        {{
            "type": "grammar_accuracy",
            "title": "Grammatical Range and Accuracy",
            "content": "Evaluation of grammatical structures and accuracy",
            "severity": "info"
        }},
        {{
            "type": "suggestion",
            "title": "Key Areas for Improvement",
            "content": "Specific, actionable suggestions for improvement",
            "severity": "suggestion"
        }}
    ]
}}

Provide only the JSON response with accurate band scores and detailed, constructive feedback."""

        return prompt
    
    def _parse_claude_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response into assessment data."""
        try:
            # Extract JSON from response (in case there's extra text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[start_idx:end_idx]
            data = json.loads(json_text)
            
            # Convert scores to Decimal
            return {
                'overall_score': Decimal(str(data['overall_score'])),
                'task_achievement': Decimal(str(data['task_achievement'])),
                'coherence_cohesion': Decimal(str(data['coherence_cohesion'])),
                'lexical_resource': Decimal(str(data['lexical_resource'])),
                'grammar_accuracy': Decimal(str(data['grammar_accuracy'])),
                'confidence': Decimal(str(data.get('confidence', 0.85))),
                'feedback': data['feedback']
            }
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse Claude response: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid response format: {e}")
    
    def _create_feedback_items(self, assessment: Assessment, feedback_data: List[Dict]):
        """Create Feedback objects from the assessment data."""
        
        for item in feedback_data:
            feedback = Feedback.objects.create(
                assessment=assessment,
                feedback_type=item['type'],
                severity=item.get('severity', 'info'),
                title=item['title'],
                content=item['content'],
                suggestion=item.get('suggestion', ''),
                highlighted_text=item.get('highlighted_text', ''),
                text_start_position=item.get('text_start_position'),
                text_end_position=item.get('text_end_position'),
                ai_confidence=Decimal(str(item.get('confidence', 0.85)))
            )
    
    def create_assessment_request(self, submission: Submission, priority: int = 0) -> AssessmentRequest:
        """Create an assessment request for queue processing."""
        
        # Check if already exists
        existing_request = AssessmentRequest.objects.filter(
            submission=submission,
            status__in=['queued', 'processing']
        ).first()
        
        if existing_request:
            return existing_request
        
        return AssessmentRequest.objects.create(
            submission=submission,
            priority=priority,
            status='queued'
        )
    
    def process_assessment_queue(self, max_requests: int = 5) -> int:
        """Process queued assessment requests."""
        
        processed_count = 0
        
        # Get queued requests ordered by priority and creation time
        queued_requests = AssessmentRequest.objects.filter(
            status='queued'
        ).select_related('submission', 'submission__task').order_by(
            '-priority', 'created_at'
        )[:max_requests]
        
        for request in queued_requests:
            try:
                # Update request status
                request.status = 'processing'
                request.processing_started_at = timezone.now()
                request.save()
                
                # Process the assessment
                assessment = self.assess_submission(request.submission)
                
                # Update request with results
                request.status = 'completed'
                request.processing_completed_at = timezone.now()
                request.assessment = assessment
                request.save()
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process assessment request {request.id}: {e}")
                
                # Update request with error
                request.status = 'failed'
                request.error_details = str(e)
                request.retry_after = timezone.now() + timedelta(minutes=30)
                request.save()
        
        return processed_count


# Service instance
assessment_service = IELTSAssessmentService()
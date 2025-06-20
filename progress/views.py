"""
Progress views with comprehensive analytics and tracking.
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Max, Min, Q
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import json

from practice.models import Submission
from assessment.models import Assessment


class ProgressDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'progress/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Basic stats
        submissions = Submission.objects.filter(user=user)
        assessments = Assessment.objects.filter(submission__user=user, status='completed')
        
        context.update({
            'total_submissions': submissions.count(),
            'total_assessments': assessments.count(),
            'average_band_score': assessments.aggregate(avg=Avg('overall_band_score'))['avg'],
        })
        
        # Score trends (last 10 assessments)
        recent_assessments = assessments.order_by('-completed_at')[:10]
        score_trend_data = []
        criteria_trends = {
            'task_achievement': [],
            'coherence_cohesion': [],
            'lexical_resource': [],
            'grammar_accuracy': []
        }
        
        for assessment in reversed(recent_assessments):
            score_trend_data.append({
                'date': assessment.completed_at.strftime('%m/%d'),
                'score': float(assessment.overall_band_score)
            })
            criteria_trends['task_achievement'].append(float(assessment.task_achievement_score))
            criteria_trends['coherence_cohesion'].append(float(assessment.coherence_cohesion_score))
            criteria_trends['lexical_resource'].append(float(assessment.lexical_resource_score))
            criteria_trends['grammar_accuracy'].append(float(assessment.grammar_accuracy_score))
        
        context['score_trend_data'] = json.dumps(score_trend_data)
        context['criteria_trends'] = json.dumps(criteria_trends)
        
        # Performance by criteria (average scores)
        criteria_performance = {
            'Task Achievement': assessments.aggregate(avg=Avg('task_achievement_score'))['avg'] or 0,
            'Coherence & Cohesion': assessments.aggregate(avg=Avg('coherence_cohesion_score'))['avg'] or 0,
            'Lexical Resource': assessments.aggregate(avg=Avg('lexical_resource_score'))['avg'] or 0,
            'Grammar & Accuracy': assessments.aggregate(avg=Avg('grammar_accuracy_score'))['avg'] or 0,
        }
        context['criteria_performance'] = criteria_performance
        
        # Identify strengths and weaknesses
        if criteria_performance:
            max_score = max(criteria_performance.values())
            min_score = min(criteria_performance.values())
            
            context['strongest_criterion'] = next(
                (k for k, v in criteria_performance.items() if v == max_score), None
            )
            context['weakest_criterion'] = next(
                (k for k, v in criteria_performance.items() if v == min_score), None
            )
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_submissions = submissions.filter(submitted_at__gte=thirty_days_ago).count()
        recent_assessments_count = assessments.filter(completed_at__gte=thirty_days_ago).count()
        
        context.update({
            'recent_submissions': recent_submissions,
            'recent_assessments': recent_assessments_count,
        })
        
        # Goal tracking
        target_band_score = getattr(user, 'target_band_score', None)
        if target_band_score and context['average_band_score']:
            progress_percentage = min(100, (context['average_band_score'] / target_band_score) * 100)
            context.update({
                'target_band_score': target_band_score,
                'progress_percentage': progress_percentage,
                'goal_gap': target_band_score - context['average_band_score']
            })
        
        # Study streak (consecutive days with submissions)
        streak = self._calculate_study_streak(user)
        context['study_streak'] = streak
        
        # Practice distribution by task type
        task_distribution = submissions.values(
            'task__task_number', 'task__module_type'
        ).annotate(count=Count('id'))
        
        context['task_distribution'] = list(task_distribution)
        
        # Improvement rate (comparing first 5 vs last 5 assessments)
        if assessments.count() >= 10:
            first_five = assessments.order_by('completed_at')[:5]
            last_five = assessments.order_by('-completed_at')[:5]
            
            first_avg = first_five.aggregate(avg=Avg('overall_band_score'))['avg']
            last_avg = last_five.aggregate(avg=Avg('overall_band_score'))['avg']
            
            if first_avg and last_avg:
                improvement = last_avg - first_avg
                context['improvement_rate'] = improvement
                context['improving'] = improvement > 0
        
        return context
    
    def _calculate_study_streak(self, user):
        """Calculate consecutive days with practice submissions."""
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        while True:
            has_submission = Submission.objects.filter(
                user=user,
                submitted_at__date=current_date
            ).exists()
            
            if has_submission:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
                
            # Limit search to prevent infinite loops
            if streak > 365:
                break
        
        return streak


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'progress/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Detailed analytics for power users
        assessments = Assessment.objects.filter(
            submission__user=user, 
            status='completed'
        ).order_by('completed_at')
        
        # Monthly progress data
        monthly_data = {}
        for assessment in assessments:
            month_key = assessment.completed_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(float(assessment.overall_band_score))
        
        # Calculate monthly averages
        monthly_averages = {
            month: sum(scores) / len(scores)
            for month, scores in monthly_data.items()
        }
        
        context['monthly_progress'] = json.dumps([
            {'month': month, 'average': avg}
            for month, avg in monthly_averages.items()
        ])
        
        return context


class GoalsView(LoginRequiredMixin, TemplateView):
    template_name = 'progress/goals.html'

#!/usr/bin/env python
"""
Script to create sample subscription plans.
"""

import os
import sys
import django

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
django.setup()

from subscriptions.models import SubscriptionPlan

def create_sample_plans():
    # Create Basic Monthly Plan
    basic_monthly = SubscriptionPlan.objects.create(
        name='Basic Monthly',
        slug='basic-monthly',
        plan_type='basic',
        billing_period='monthly',
        price=19.99,
        currency='USD',
        assessment_credits=20,
        practice_tasks_limit=None,
        priority_support=False,
        advanced_analytics=False,
        description='Perfect for getting started with IELTS writing practice',
        features=[
            '20 AI assessments per month',
            'Unlimited practice tasks',
            'Basic feedback and scoring',
            'Progress tracking',
            'Email support'
        ],
        is_active=True,
        is_featured=False,
        sort_order=1
    )

    # Create Premium Monthly Plan
    premium_monthly = SubscriptionPlan.objects.create(
        name='Premium Monthly',
        slug='premium-monthly',
        plan_type='premium',
        billing_period='monthly',
        price=39.99,
        currency='USD',
        assessment_credits=50,
        practice_tasks_limit=None,
        priority_support=True,
        advanced_analytics=True,
        description='Most popular plan with comprehensive features',
        features=[
            '50 AI assessments per month',
            'Unlimited practice tasks',
            'Detailed feedback and suggestions',
            'Advanced analytics and insights',
            'Priority email support',
            'Performance tracking'
        ],
        is_active=True,
        is_featured=True,
        sort_order=2
    )

    # Create Pro Annual Plan
    pro_annual = SubscriptionPlan.objects.create(
        name='Pro Annual',
        slug='pro-annual',
        plan_type='pro',
        billing_period='annual',
        price=399.99,
        currency='USD',
        assessment_credits=100,
        practice_tasks_limit=None,
        priority_support=True,
        advanced_analytics=True,
        description='Best value for serious IELTS candidates',
        features=[
            '100 AI assessments per month',
            'Unlimited practice tasks',
            'Premium feedback with inline comments',
            'Advanced analytics and insights',
            'Priority support with phone access',
            'Performance tracking and reporting',
            'Export detailed reports',
            'Early access to new features'
        ],
        is_active=True,
        is_featured=False,
        sort_order=3
    )

    print(f'Created {SubscriptionPlan.objects.count()} subscription plans:')
    for plan in SubscriptionPlan.objects.all():
        print(f'- {plan.name}: ${plan.price}/{plan.billing_period} - {plan.assessment_credits} credits')

if __name__ == '__main__':
    create_sample_plans()
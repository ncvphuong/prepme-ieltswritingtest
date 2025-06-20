"""
Subscription and payment models for IELTS Writing Test platform.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import stripe
from django.conf import settings

from core.models import BaseModel

User = get_user_model()


class SubscriptionPlan(BaseModel):
    """
    Available subscription plans.
    """
    PLAN_TYPE_CHOICES = [
        ('basic', 'Basic Plan'),
        ('premium', 'Premium Plan'),
        ('pro', 'Pro Plan'),
    ]
    
    BILLING_PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', '3 Months'),
        ('biannual', '6 Months'),
        ('annual', 'Annual'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIOD_CHOICES)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Features
    assessment_credits = models.PositiveIntegerField(
        help_text="Number of AI assessments included"
    )
    practice_tasks_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum practice tasks (null = unlimited)"
    )
    priority_support = models.BooleanField(default=False)
    advanced_analytics = models.BooleanField(default=False)
    
    # Stripe integration
    stripe_price_id = models.CharField(max_length=100, blank=True)
    stripe_product_id = models.CharField(max_length=100, blank=True)
    
    # Plan settings
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    description = models.TextField(blank=True)
    features = models.JSONField(
        default=list,
        help_text="List of features for this plan"
    )
    
    def __str__(self):
        return f"{self.name} - {self.get_billing_period_display()}"
    
    @property
    def monthly_price(self):
        """Calculate equivalent monthly price."""
        if self.billing_period == 'monthly':
            return self.price
        elif self.billing_period == 'quarterly':
            return self.price / 3
        elif self.billing_period == 'biannual':
            return self.price / 6
        elif self.billing_period == 'annual':
            return self.price / 12
        return self.price
    
    @property
    def savings_percentage(self):
        """Calculate savings compared to monthly billing."""
        if self.billing_period == 'monthly':
            return 0
        
        # Find monthly equivalent plan
        try:
            monthly_plan = SubscriptionPlan.objects.get(
                plan_type=self.plan_type,
                billing_period='monthly',
                is_active=True
            )
            monthly_total = monthly_plan.price * self.billing_months
            savings = (monthly_total - self.price) / monthly_total * 100
            return max(0, savings)
        except SubscriptionPlan.DoesNotExist:
            return 0
    
    @property
    def billing_months(self):
        """Number of months this plan covers."""
        if self.billing_period == 'monthly':
            return 1
        elif self.billing_period == 'quarterly':
            return 3
        elif self.billing_period == 'biannual':
            return 6
        elif self.billing_period == 'annual':
            return 12
        return 1
    
    class Meta:
        db_table = 'subscriptions_plan'
        ordering = ['sort_order', 'price']
        indexes = [
            models.Index(fields=['is_active', 'plan_type']),
            models.Index(fields=['billing_period']),
        ]


class UserSubscription(BaseModel):
    """
    User's active subscription.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('past_due', 'Past Due'),
        ('unpaid', 'Unpaid'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    
    # Subscription status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Billing cycle
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_end = models.DateTimeField(null=True, blank=True)
    
    # Usage tracking
    assessment_credits_used = models.PositiveIntegerField(default=0)
    assessment_credits_remaining = models.PositiveIntegerField(default=0)
    
    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Auto-renewal
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
    
    @property
    def is_active(self):
        """Check if subscription is currently active."""
        return (
            self.status == 'active' and
            self.current_period_end > timezone.now()
        )
    
    @property
    def is_trial(self):
        """Check if subscription is in trial period."""
        return (
            self.trial_end and
            self.trial_end > timezone.now()
        )
    
    @property
    def days_remaining(self):
        """Days remaining in current period."""
        if self.current_period_end <= timezone.now():
            return 0
        return (self.current_period_end - timezone.now()).days
    
    def use_assessment_credit(self):
        """Use one assessment credit."""
        if self.assessment_credits_remaining > 0:
            self.assessment_credits_used += 1
            self.assessment_credits_remaining -= 1
            self.save()
            return True
        return False
    
    def reset_usage(self):
        """Reset usage for new billing period."""
        self.assessment_credits_used = 0
        self.assessment_credits_remaining = self.plan.assessment_credits
        self.save()
    
    def cancel_subscription(self):
        """Cancel subscription at period end."""
        self.cancel_at_period_end = True
        self.canceled_at = timezone.now()
        self.save()
        
        # Cancel in Stripe if exists
        if self.stripe_subscription_id:
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.Subscription.modify(
                    self.stripe_subscription_id,
                    cancel_at_period_end=True
                )
            except stripe.error.StripeError as e:
                # Log error but don't fail
                pass
    
    class Meta:
        db_table = 'subscriptions_user_subscription'
        indexes = [
            models.Index(fields=['status', 'current_period_end']),
            models.Index(fields=['stripe_subscription_id']),
        ]


class PaymentHistory(BaseModel):
    """
    Record of all payments.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Stripe integration
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    
    # Payment metadata
    payment_method = models.CharField(max_length=50, blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Billing period covered
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - ${self.amount}"
    
    class Meta:
        db_table = 'subscriptions_payment_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]


class UsageRecord(BaseModel):
    """
    Track detailed usage for analytics and billing.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )
    subscription = models.ForeignKey(
        UserSubscription,
        on_delete=models.CASCADE,
        related_name='usage_records',
        null=True,
        blank=True
    )
    
    # Usage type
    USAGE_TYPE_CHOICES = [
        ('assessment', 'AI Assessment'),
        ('practice', 'Practice Session'),
        ('export', 'Data Export'),
    ]
    
    usage_type = models.CharField(max_length=20, choices=USAGE_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    
    # Context
    description = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Billing
    billable = models.BooleanField(default=True)
    billed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_usage_type_display()} - {self.created_at}"
    
    class Meta:
        db_table = 'subscriptions_usage_record'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'usage_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['billable', 'billed_at']),
        ]
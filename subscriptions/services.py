"""
Stripe payment processing service.
"""

import stripe
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from .models import SubscriptionPlan, UserSubscription, PaymentHistory, UsageRecord

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe payment operations."""
    
    def __init__(self):
        self.stripe = stripe
    
    def create_customer(self, user):
        """Create a Stripe customer for a user."""
        try:
            customer = self.stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip() or user.username,
                metadata={
                    'user_id': str(user.id),
                    'username': user.username,
                }
            )
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer for user {user.id}: {e}")
            raise
    
    def create_checkout_session(self, user, plan, success_url, cancel_url):
        """Create a Stripe Checkout session for subscription."""
        try:
            # Create or get customer
            customer = self.get_or_create_customer(user)
            
            checkout_session = self.stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(user.id),
                    'plan_id': str(plan.id),
                },
                allow_promotion_codes=True,
                billing_address_collection='required',
                subscription_data={
                    'metadata': {
                        'user_id': str(user.id),
                        'plan_id': str(plan.id),
                    }
                }
            )
            return checkout_session
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session for user {user.id}, plan {plan.id}: {e}")
            raise
    
    def get_or_create_customer(self, user):
        """Get existing Stripe customer or create new one."""
        try:
            # Check if user has existing subscription with customer ID
            subscription = getattr(user, 'subscription', None)
            if subscription and subscription.stripe_customer_id:
                try:
                    customer = self.stripe.Customer.retrieve(subscription.stripe_customer_id)
                    return customer
                except stripe.error.InvalidRequestError:
                    # Customer doesn't exist, create new one
                    pass
            
            # Search for existing customer by email
            customers = self.stripe.Customer.list(email=user.email, limit=1)
            if customers.data:
                return customers.data[0]
            
            # Create new customer
            return self.create_customer(user)
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get or create customer for user {user.id}: {e}")
            raise
    
    def handle_successful_payment(self, stripe_subscription):
        """Handle successful subscription payment."""
        try:
            logger.info(f"Processing subscription {stripe_subscription.id}")
            metadata = stripe_subscription.metadata
            user_id = metadata.get('user_id')
            plan_id = metadata.get('plan_id')
            
            logger.info(f"Metadata: user_id={user_id}, plan_id={plan_id}")
            
            if not user_id or not plan_id:
                logger.error(f"Missing metadata in subscription {stripe_subscription.id}: {metadata}")
                return None
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            user = User.objects.get(id=user_id)
            plan = SubscriptionPlan.objects.get(id=plan_id)
            
            # Get billing period from latest invoice
            from datetime import datetime, timezone as dt_timezone
            try:
                invoice = self.stripe.Invoice.retrieve(stripe_subscription.latest_invoice)
                current_period_start = datetime.fromtimestamp(
                    invoice.period_start,
                    tz=dt_timezone.utc
                )
                current_period_end = datetime.fromtimestamp(
                    invoice.period_end,
                    tz=dt_timezone.utc
                )
                
                # If period start and end are the same, it's immediate billing
                # Calculate proper period based on plan
                if current_period_start == current_period_end:
                    logger.info("Same period start/end detected, calculating billing cycle")
                    current_period_start = datetime.fromtimestamp(
                        stripe_subscription.created,
                        tz=dt_timezone.utc
                    )
                    from dateutil.relativedelta import relativedelta
                    current_period_end = current_period_start + relativedelta(months=plan.billing_months)
                
                logger.info(f"Billing period: {current_period_start} to {current_period_end}")
            except Exception as e:
                logger.error(f"Error getting billing period from invoice: {e}")
                # Fallback to subscription dates
                current_period_start = datetime.fromtimestamp(
                    stripe_subscription.created,
                    tz=dt_timezone.utc
                )
                from dateutil.relativedelta import relativedelta
                current_period_end = current_period_start + relativedelta(months=1)
                logger.info(f"Using fallback period: {current_period_start} to {current_period_end}")
            
            # Create or update subscription
            subscription, created = UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'status': 'active',
                    'current_period_start': current_period_start,
                    'current_period_end': current_period_end,
                    'stripe_subscription_id': stripe_subscription.id,
                    'stripe_customer_id': stripe_subscription.customer,
                    'assessment_credits_remaining': plan.assessment_credits,
                    'assessment_credits_used': 0,
                    'cancel_at_period_end': False,
                    'canceled_at': None,
                }
            )
            
            logger.info(f"{'Created' if created else 'Updated'} subscription {subscription.id} for user {user.id}")
            
            # Create payment record (reuse invoice from above)
            payment = PaymentHistory.objects.create(
                user=user,
                subscription=subscription,
                plan=plan,
                amount=Decimal(invoice.amount_paid / 100),  # Convert from cents
                currency=invoice.currency.upper(),
                status='succeeded',
                stripe_payment_intent_id=getattr(invoice, 'payment_intent', '') or '',
                stripe_invoice_id=invoice.id,
                period_start=current_period_start,
                period_end=current_period_end,
            )
            
            logger.info(f"Successfully processed subscription for user {user.id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to handle successful payment: {e}")
            raise
    
    def cancel_subscription(self, subscription):
        """Cancel a subscription in Stripe."""
        try:
            if subscription.stripe_subscription_id:
                self.stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                
                subscription.cancel_at_period_end = True
                subscription.canceled_at = timezone.now()
                subscription.save()
                
                logger.info(f"Canceled subscription {subscription.id}")
                return True
            return False
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription {subscription.id}: {e}")
            raise
    
    def create_billing_portal_session(self, user, return_url):
        """Create a Stripe billing portal session."""
        try:
            subscription = getattr(user, 'subscription', None)
            if not subscription or not subscription.stripe_customer_id:
                raise ValueError("User has no active subscription")
            
            session = self.stripe.billing_portal.Session.create(
                customer=subscription.stripe_customer_id,
                return_url=return_url,
            )
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session for user {user.id}: {e}")
            raise
    
    def sync_subscription_status(self, subscription):
        """Sync subscription status with Stripe."""
        try:
            if not subscription.stripe_subscription_id:
                return subscription
            
            stripe_sub = self.stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            
            # Update status
            status_mapping = {
                'active': 'active',
                'canceled': 'canceled',
                'past_due': 'past_due',
                'unpaid': 'unpaid',
                'paused': 'paused',
            }
            
            subscription.status = status_mapping.get(stripe_sub.status, subscription.status)
            
            # Get billing period from latest invoice (same fix as payment processing)
            from datetime import datetime, timezone as dt_timezone
            try:
                invoice = self.stripe.Invoice.retrieve(stripe_sub.latest_invoice)
                current_period_start = datetime.fromtimestamp(
                    invoice.period_start,
                    tz=dt_timezone.utc
                )
                current_period_end = datetime.fromtimestamp(
                    invoice.period_end,
                    tz=dt_timezone.utc
                )
                
                # Handle immediate billing where periods are the same
                if current_period_start == current_period_end:
                    current_period_start = datetime.fromtimestamp(
                        stripe_sub.created,
                        tz=dt_timezone.utc
                    )
                    from dateutil.relativedelta import relativedelta
                    current_period_end = current_period_start + relativedelta(months=subscription.plan.billing_months)
                
                subscription.current_period_start = current_period_start
                subscription.current_period_end = current_period_end
                
            except Exception as e:
                logger.error(f"Error syncing billing period: {e}")
                # Keep existing dates if sync fails
                pass
            
            subscription.cancel_at_period_end = stripe_sub.cancel_at_period_end
            
            subscription.save()
            return subscription
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to sync subscription {subscription.id}: {e}")
            return subscription


class UsageService:
    """Service for tracking usage and credits."""
    
    @staticmethod
    def can_use_assessment(user):
        """Check if user can use an assessment credit."""
        subscription = getattr(user, 'subscription', None)
        if not subscription:
            return False, "No active subscription"
        
        if not subscription.is_active:
            return False, "Subscription is not active"
        
        if subscription.assessment_credits_remaining <= 0:
            return False, "No assessment credits remaining"
        
        return True, "OK"
    
    @staticmethod
    def use_assessment_credit(user, assessment=None):
        """Use an assessment credit and track usage."""
        can_use, reason = UsageService.can_use_assessment(user)
        if not can_use:
            return False, reason
        
        subscription = user.subscription
        success = subscription.use_assessment_credit()
        
        if success:
            # Track usage
            UsageRecord.objects.create(
                user=user,
                subscription=subscription,
                usage_type='assessment',
                description=f"AI Assessment for submission {assessment.submission.id if assessment else 'N/A'}",
                metadata={
                    'assessment_id': assessment.id if assessment else None,
                    'submission_id': assessment.submission.id if assessment else None,
                }
            )
            
        return success, "Assessment credit used" if success else "Failed to use credit"
    
    @staticmethod
    def get_usage_stats(user, days=30):
        """Get usage statistics for a user."""
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        usage_records = UsageRecord.objects.filter(
            user=user,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        stats = {
            'total_assessments': usage_records.filter(usage_type='assessment').count(),
            'total_practices': usage_records.filter(usage_type='practice').count(),
            'daily_usage': {},
        }
        
        # Calculate daily usage
        current_date = start_date.date()
        while current_date <= end_date.date():
            day_usage = usage_records.filter(
                created_at__date=current_date
            ).count()
            stats['daily_usage'][current_date.isoformat()] = day_usage
            current_date += timedelta(days=1)
        
        return stats


# Service instances
stripe_service = StripeService()
usage_service = UsageService()
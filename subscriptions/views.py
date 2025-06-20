"""
Subscription and payment views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, TemplateView
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings
import stripe
import json
import logging

from .models import SubscriptionPlan, UserSubscription, PaymentHistory
from .services import stripe_service, usage_service

logger = logging.getLogger(__name__)


class SubscriptionPlansView(TemplateView):
    """Display available subscription plans."""
    template_name = 'subscriptions/plans.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active plans grouped by type
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order', 'price')
        
        context['plans'] = plans
        context['user_subscription'] = None
        
        if self.request.user.is_authenticated:
            context['user_subscription'] = getattr(self.request.user, 'subscription', None)
        
        return context


class UserSubscriptionView(LoginRequiredMixin, TemplateView):
    """Display user's current subscription and billing."""
    template_name = 'subscriptions/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        subscription = getattr(self.request.user, 'subscription', None)
        context['subscription'] = subscription
        
        if subscription:
            # Get recent payments
            context['recent_payments'] = PaymentHistory.objects.filter(
                user=self.request.user
            ).order_by('-created_at')[:10]
            
            # Get usage stats
            context['usage_stats'] = usage_service.get_usage_stats(self.request.user)
            
            # Sync with Stripe
            stripe_service.sync_subscription_status(subscription)
        
        return context


class ManageSubscriptionView(LoginRequiredMixin, TemplateView):
    """Detailed subscription management page."""
    template_name = 'subscriptions/manage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        subscription = getattr(self.request.user, 'subscription', None)
        context['subscription'] = subscription
        
        if subscription:
            # Get recent payments
            context['recent_payments'] = PaymentHistory.objects.filter(
                user=self.request.user
            ).order_by('-created_at')[:10]
            
            # Get usage stats
            context['usage_stats'] = usage_service.get_usage_stats(self.request.user)
            
            # Sync with Stripe to ensure data is current
            stripe_service.sync_subscription_status(subscription)
            
            # Calculate days remaining
            if subscription.current_period_end:
                days_remaining = (subscription.current_period_end - timezone.now().date()).days
                context['days_remaining'] = max(0, days_remaining)
            else:
                context['days_remaining'] = 0
        
        return context


@login_required
def checkout(request, plan_id):
    """Create Stripe checkout session."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Check if user already has active subscription
    existing_subscription = getattr(request.user, 'subscription', None)
    if existing_subscription and existing_subscription.is_active:
        messages.warning(request, 'You already have an active subscription.')
        return redirect('subscriptions:dashboard')
    
    try:
        # Create checkout session
        success_url = request.build_absolute_uri(reverse('subscriptions:success'))
        cancel_url = request.build_absolute_uri(reverse('subscriptions:plans'))
        
        checkout_session = stripe_service.create_checkout_session(
            user=request.user,
            plan=plan,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return redirect(checkout_session.url)
        
    except Exception as e:
        logger.error(f"Checkout failed for user {request.user.id}, plan {plan.id}: {e}")
        messages.error(request, 'Payment processing failed. Please try again.')
        return redirect('subscriptions:plans')


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """Payment success page."""
    template_name = 'subscriptions/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sync subscription to ensure it's up to date
        subscription = getattr(self.request.user, 'subscription', None)
        if subscription:
            stripe_service.sync_subscription_status(subscription)
            context['subscription'] = subscription
        
        return context


@login_required
def cancel_subscription(request):
    """Cancel user's subscription."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    subscription = getattr(request.user, 'subscription', None)
    if not subscription:
        return JsonResponse({'error': 'No active subscription'}, status=400)
    
    try:
        stripe_service.cancel_subscription(subscription)
        messages.success(request, 'Your subscription has been canceled and will not renew.')
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Failed to cancel subscription for user {request.user.id}: {e}")
        return JsonResponse({'error': 'Failed to cancel subscription'}, status=500)


@login_required
def billing_portal(request):
    """Redirect to Stripe billing portal."""
    subscription = getattr(request.user, 'subscription', None)
    if not subscription:
        messages.error(request, 'No active subscription found.')
        return redirect('subscriptions:plans')
    
    try:
        return_url = request.build_absolute_uri(reverse('subscriptions:dashboard'))
        session = stripe_service.create_billing_portal_session(
            user=request.user,
            return_url=return_url
        )
        return redirect(session.url)
        
    except Exception as e:
        logger.error(f"Failed to create billing portal for user {request.user.id}: {e}")
        messages.error(request, 'Unable to access billing portal. Please try again.')
        return redirect('subscriptions:dashboard')


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logger.error("Invalid payload in Stripe webhook")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature in Stripe webhook")
        return HttpResponse(status=400)
    
    # Handle the event
    try:
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_checkout_completed(session)
            
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            handle_payment_succeeded(invoice)
            
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            handle_payment_failed(invoice)
            
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            handle_subscription_updated(subscription)
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            handle_subscription_deleted(subscription)
            
        else:
            logger.info(f"Unhandled Stripe event type: {event['type']}")
    
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {e}")
        return HttpResponse(status=500)
    
    return HttpResponse(status=200)


def handle_checkout_completed(session):
    """Handle successful checkout completion."""
    if session.mode == 'subscription':
        subscription_id = session.subscription
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        stripe_service.handle_successful_payment(stripe_subscription)


def handle_payment_succeeded(invoice):
    """Handle successful invoice payment."""
    if invoice.subscription:
        subscription_id = invoice.subscription
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update subscription if needed
        try:
            user_subscription = UserSubscription.objects.get(
                stripe_subscription_id=subscription_id
            )
            stripe_service.sync_subscription_status(user_subscription)
            
            # Reset usage for new billing period if this is a renewal
            if user_subscription.status == 'active':
                user_subscription.reset_usage()
                
        except UserSubscription.DoesNotExist:
            logger.warning(f"No local subscription found for Stripe subscription {subscription_id}")


def handle_payment_failed(invoice):
    """Handle failed invoice payment."""
    if invoice.subscription:
        try:
            subscription = UserSubscription.objects.get(
                stripe_subscription_id=invoice.subscription
            )
            subscription.status = 'past_due'
            subscription.save()
            
            logger.info(f"Marked subscription {subscription.id} as past due")
            
        except UserSubscription.DoesNotExist:
            logger.warning(f"No local subscription found for failed payment {invoice.id}")


def handle_subscription_updated(stripe_subscription):
    """Handle subscription updates from Stripe."""
    try:
        subscription = UserSubscription.objects.get(
            stripe_subscription_id=stripe_subscription.id
        )
        stripe_service.sync_subscription_status(subscription)
        
    except UserSubscription.DoesNotExist:
        logger.warning(f"No local subscription found for Stripe subscription {stripe_subscription.id}")


def handle_subscription_deleted(stripe_subscription):
    """Handle subscription cancellation from Stripe."""
    try:
        subscription = UserSubscription.objects.get(
            stripe_subscription_id=stripe_subscription.id
        )
        subscription.status = 'canceled'
        subscription.canceled_at = timezone.now()
        subscription.save()
        
        logger.info(f"Canceled subscription {subscription.id}")
        
    except UserSubscription.DoesNotExist:
        logger.warning(f"No local subscription found for canceled Stripe subscription {stripe_subscription.id}")


@login_required
def usage_api(request):
    """API endpoint for usage statistics."""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)
    
    subscription = getattr(request.user, 'subscription', None)
    if not subscription:
        return JsonResponse({'error': 'No subscription found'}, status=404)
    
    stats = usage_service.get_usage_stats(request.user)
    
    return JsonResponse({
        'subscription': {
            'plan': subscription.plan.name,
            'status': subscription.status,
            'credits_remaining': subscription.assessment_credits_remaining,
            'credits_used': subscription.assessment_credits_used,
            'period_end': subscription.current_period_end.isoformat(),
        },
        'usage': stats
    })


# Legacy aliases for existing URL patterns
CheckoutView = TemplateView
ManageSubscriptionView = UserSubscriptionView
BillingHistoryView = UserSubscriptionView
StripeWebhookView = TemplateView

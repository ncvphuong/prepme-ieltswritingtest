"""
Subscriptions views - placeholder implementations.
"""
from django.views.generic import TemplateView


class SubscriptionPlansView(TemplateView):
    template_name = 'subscriptions/plans.html'


class CheckoutView(TemplateView):
    template_name = 'subscriptions/checkout.html'


class ManageSubscriptionView(TemplateView):
    template_name = 'subscriptions/manage.html'


class BillingHistoryView(TemplateView):
    template_name = 'subscriptions/billing.html'


class StripeWebhookView(TemplateView):
    template_name = 'subscriptions/webhook.html'

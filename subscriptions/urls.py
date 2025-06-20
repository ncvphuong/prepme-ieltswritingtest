"""
URL patterns for subscriptions app.
"""

from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Plan selection and subscription management
    path('plans/', views.SubscriptionPlansView.as_view(), name='plans'),
    path('dashboard/', views.UserSubscriptionView.as_view(), name='dashboard'),
    path('manage/', views.ManageSubscriptionView.as_view(), name='manage'),
    
    # Checkout and payment flow
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    
    # Subscription management
    path('cancel/', views.cancel_subscription, name='cancel'),
    path('billing-portal/', views.billing_portal, name='billing_portal'),
    
    # API endpoints
    path('usage/', views.usage_api, name='usage_api'),
    
    # Stripe webhook
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
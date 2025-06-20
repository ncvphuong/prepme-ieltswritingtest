"""
URL configuration for subscriptions app.
"""
from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.SubscriptionPlansView.as_view(), name='plans'),
    path('checkout/<int:plan_id>/', views.CheckoutView.as_view(), name='checkout'),
    path('manage/', views.ManageSubscriptionView.as_view(), name='manage'),
    path('billing/', views.BillingHistoryView.as_view(), name='billing'),
    path('webhook/', views.StripeWebhookView.as_view(), name='webhook'),
]
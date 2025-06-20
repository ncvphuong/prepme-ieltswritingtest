#!/usr/bin/env python
"""
Test script for Stripe integration with local development.
"""

import os
import sys
import django
import stripe
from decimal import Decimal

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
django.setup()

from subscriptions.models import SubscriptionPlan
from django.contrib.auth import get_user_model
from subscriptions.services import stripe_service
from django.conf import settings

User = get_user_model()

def test_stripe_connection():
    """Test basic Stripe connection."""
    print("🔍 Testing Stripe connection...")
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Test basic API call
        products = stripe.Product.list(limit=3)
        print(f"✅ Stripe connection successful! Found {len(products.data)} products.")
        return True
    except Exception as e:
        print(f"❌ Stripe connection failed: {e}")
        return False

def test_subscription_plans():
    """Test subscription plans in database."""
    print("\n📋 Testing subscription plans...")
    try:
        plans = SubscriptionPlan.objects.filter(is_active=True)
        print(f"✅ Found {plans.count()} active subscription plans:")
        
        for plan in plans:
            print(f"   - {plan.name}: ${plan.price}/{plan.billing_period}")
            print(f"     Features: {len(plan.features)} features")
            print(f"     Credits: {plan.assessment_credits}")
        
        return plans.count() > 0
    except Exception as e:
        print(f"❌ Subscription plans test failed: {e}")
        return False

def test_user_creation():
    """Test user creation and subscription assignment."""
    print("\n👤 Testing user creation...")
    try:
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print(f"✅ Created new test user: {user.username}")
        else:
            print(f"✅ Using existing test user: {user.username}")
        
        return user
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return None

def test_webhook_endpoint():
    """Test webhook endpoint availability."""
    print("\n🎣 Testing webhook endpoint...")
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        webhook_url = reverse('subscriptions:stripe_webhook')
        print(f"✅ Webhook endpoint available at: {webhook_url}")
        print(f"   Full URL: http://localhost:8000{webhook_url}")
        
        return True
    except Exception as e:
        print(f"❌ Webhook endpoint test failed: {e}")
        return False

def display_test_instructions():
    """Display instructions for manual testing."""
    print("\n" + "="*60)
    print("🧪 MANUAL TESTING INSTRUCTIONS")
    print("="*60)
    
    print("\n1. 🎣 WEBHOOK LISTENER:")
    print("   Run this in a separate terminal:")
    print("   stripe listen --forward-to localhost:8000/subscriptions/webhook/")
    
    print("\n2. 🌐 ACCESS THE APPLICATION:")
    print("   Open your browser and go to:")
    print("   http://localhost:8000/subscriptions/plans/")
    
    print("\n3. 💳 TEST SUBSCRIPTION FLOW:")
    print("   a) Register a new user or login")
    print("   b) Click on a subscription plan")
    print("   c) Use Stripe test card: 4242 4242 4242 4242")
    print("   d) Expiry: Any future date (e.g., 12/34)")
    print("   e) CVC: Any 3 digits (e.g., 123)")
    
    print("\n4. 🔍 MONITOR WEBHOOKS:")
    print("   Watch the Stripe CLI terminal for webhook events")
    print("   Check Django logs for webhook processing")
    
    print("\n5. 📊 TEST DASHBOARD:")
    print("   After successful payment, visit:")
    print("   http://localhost:8000/subscriptions/dashboard/")
    
    print("\n6. 🎯 TRIGGER TEST EVENTS:")
    print("   stripe trigger checkout.session.completed")
    print("   stripe trigger invoice.payment_succeeded")
    print("   stripe trigger customer.subscription.updated")
    
    print("\n" + "="*60)

def main():
    """Run all tests."""
    print("🚀 STRIPE INTEGRATION TEST SUITE")
    print("="*50)
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_stripe_connection():
        tests_passed += 1
    
    if test_subscription_plans():
        tests_passed += 1
    
    if test_user_creation():
        tests_passed += 1
    
    if test_webhook_endpoint():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! Your Stripe integration is ready.")
        display_test_instructions()
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return tests_passed == total_tests

if __name__ == '__main__':
    main()
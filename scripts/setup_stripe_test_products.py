#!/usr/bin/env python
"""
Create Stripe test products and prices for development environment.
"""

import os
import sys
import django
import stripe

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
django.setup()

from django.conf import settings
from subscriptions.models import SubscriptionPlan

def create_stripe_test_products():
    """Create test products and prices in Stripe."""
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    print("🧪 CREATING STRIPE TEST PRODUCTS")
    print("=" * 50)
    print(f"Using Stripe key: {settings.STRIPE_SECRET_KEY[:20]}...")
    
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')
    
    for plan in plans:
        print(f"\n📦 Creating product for: {plan.name}")
        print(f"   Price: ${plan.price} per {plan.billing_period}")
        print(f"   Credits: {plan.assessment_credits}")
        
        try:
            # Create product in Stripe
            product = stripe.Product.create(
                name=plan.name,
                description=plan.description,
                metadata={
                    'plan_id': str(plan.id),
                    'plan_type': plan.plan_type,
                    'assessment_credits': str(plan.assessment_credits),
                    'environment': 'test'
                }
            )
            
            # Determine interval for recurring price
            if plan.billing_period == 'monthly':
                interval = 'month'
                interval_count = 1
            elif plan.billing_period == 'annual':
                interval = 'year'
                interval_count = 1
            elif plan.billing_period == 'quarterly':
                interval = 'month'
                interval_count = 3
            elif plan.billing_period == 'biannual':
                interval = 'month'
                interval_count = 6
            else:
                interval = 'month'
                interval_count = 1
            
            # Create price in Stripe
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(plan.price * 100),  # Convert to cents
                currency=plan.currency.lower(),
                recurring={
                    'interval': interval,
                    'interval_count': interval_count
                },
                metadata={
                    'plan_id': str(plan.id),
                    'billing_period': plan.billing_period,
                    'environment': 'test'
                }
            )
            
            # Update local plan with Stripe IDs
            plan.stripe_product_id = product.id
            plan.stripe_price_id = price.id
            plan.save()
            
            print(f"   ✅ Created Stripe product: {product.id}")
            print(f"   ✅ Created Stripe price: {price.id}")
            print(f"   ✅ Updated local plan with Stripe IDs")
            
        except Exception as e:
            print(f"   ❌ Error creating product for {plan.name}: {e}")
            continue
    
    print(f"\n🎉 STRIPE TEST SETUP COMPLETE!")
    
    # Verify all plans have stripe_price_id
    plans_without_stripe = SubscriptionPlan.objects.filter(
        is_active=True, 
        stripe_price_id__in=['', None]
    )
    
    if plans_without_stripe.exists():
        print(f"⚠️  Warning: {plans_without_stripe.count()} plans still missing Stripe price IDs")
        for plan in plans_without_stripe:
            print(f"   - {plan.name}")
    else:
        print("✅ All active plans now have Stripe price IDs!")
        
        # Show updated plans
        print("\n📋 UPDATED SUBSCRIPTION PLANS:")
        for plan in SubscriptionPlan.objects.filter(is_active=True):
            print(f"   {plan.name}: {plan.stripe_price_id}")

def test_checkout_session():
    """Test creating a checkout session with the new prices."""
    print(f"\n🧪 TESTING CHECKOUT SESSION CREATION")
    print("=" * 50)
    
    try:
        from django.contrib.auth import get_user_model
        from subscriptions.services import stripe_service
        
        User = get_user_model()
        plan = SubscriptionPlan.objects.filter(is_active=True, stripe_price_id__isnull=False).first()
        
        if not plan:
            print("❌ No plans with stripe_price_id found")
            return
            
        # Create test user if doesn't exist
        user, created = User.objects.get_or_create(
            username='testuser2',
            defaults={
                'email': 'test2@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        print(f"Using plan: {plan.name} (price_id: {plan.stripe_price_id})")
        print(f"Using user: {user.username}")
        
        # Test checkout session creation
        checkout_session = stripe_service.create_checkout_session(
            user=user,
            plan=plan,
            success_url='http://localhost:8000/subscriptions/success/',
            cancel_url='http://localhost:8000/subscriptions/plans/'
        )
        
        print(f"✅ Checkout session created successfully!")
        print(f"   Session ID: {checkout_session.id}")
        print(f"   URL: {checkout_session.url}")
        
    except Exception as e:
        print(f"❌ Error testing checkout session: {e}")

if __name__ == '__main__':
    create_stripe_test_products()
    test_checkout_session()
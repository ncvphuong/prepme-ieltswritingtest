#!/usr/bin/env python
"""
PRODUCTION Stripe products and prices setup script.

⚠️  IMPORTANT: Only run this on production server with LIVE Stripe keys!

This script will:
1. Connect to your production Django database
2. Use your LIVE Stripe keys to create products
3. Update your production subscription plans with live Stripe IDs

Usage:
    python scripts/setup_production_stripe.py
"""

import os
import sys
import django

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django for PRODUCTION
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.production')
django.setup()

import stripe
from django.conf import settings
from subscriptions.models import SubscriptionPlan

def verify_production_environment():
    """Ensure we're in production mode with live keys."""
    print("🔍 VERIFYING PRODUCTION ENVIRONMENT")
    print("=" * 50)
    
    # Check DEBUG is False
    if settings.DEBUG:
        print("❌ ERROR: DEBUG=True detected!")
        print("   This script should only run in production with DEBUG=False")
        return False
    
    # Check for live Stripe keys
    if not settings.STRIPE_SECRET_KEY.startswith('sk_live_'):
        print("❌ ERROR: Not using live Stripe keys!")
        print(f"   Current key starts with: {settings.STRIPE_SECRET_KEY[:15]}...")
        print("   Production requires keys starting with 'sk_live_'")
        return False
    
    print("✅ DEBUG=False ✓")
    print("✅ Live Stripe keys detected ✓")
    print(f"✅ Secret key: {settings.STRIPE_SECRET_KEY[:15]}...")
    
    return True

def create_production_stripe_products():
    """Create production products and prices in Stripe."""
    
    if not verify_production_environment():
        print("\n❌ PRODUCTION VERIFICATION FAILED - ABORTING")
        return False
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    print(f"\n🏭 CREATING LIVE STRIPE PRODUCTS")
    print("=" * 50)
    print("⚠️  WARNING: This will create LIVE products in Stripe!")
    print("⚠️  Real customers will be able to purchase these!")
    
    # Safety confirmation
    confirmation = input("\nType 'CREATE LIVE PRODUCTS' to proceed: ")
    if confirmation != 'CREATE LIVE PRODUCTS':
        print("❌ Confirmation failed - aborting")
        return False
    
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')
    
    if not plans.exists():
        print("❌ No active subscription plans found!")
        print("   Run 'python scripts/create_plans.py' first")
        return False
    
    print(f"\nFound {plans.count()} active subscription plans to create")
    
    created_products = []
    
    for plan in plans:
        print(f"\n📦 Creating LIVE product: {plan.name}")
        print(f"   💰 Price: ${plan.price} per {plan.billing_period}")
        print(f"   🎯 Credits: {plan.assessment_credits}")
        
        try:
            # Create product in Stripe LIVE environment
            product = stripe.Product.create(
                name=plan.name,
                description=plan.description,
                metadata={
                    'plan_id': str(plan.id),
                    'plan_type': plan.plan_type,
                    'assessment_credits': str(plan.assessment_credits),
                    'environment': 'production',
                    'created_by': 'django_script'
                }
            )
            
            # Determine billing interval
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
                # Default to monthly
                interval = 'month'
                interval_count = 1
            
            # Create price in Stripe LIVE environment
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
                    'environment': 'production',
                    'created_by': 'django_script'
                }
            )
            
            # Update local plan with LIVE Stripe IDs
            plan.stripe_product_id = product.id
            plan.stripe_price_id = price.id
            plan.save()
            
            created_products.append({
                'plan': plan,
                'product_id': product.id,
                'price_id': price.id
            })
            
            print(f"   ✅ Product: {product.id}")
            print(f"   ✅ Price: {price.id}")
            print(f"   ✅ Updated database")
            
        except Exception as e:
            print(f"   ❌ ERROR creating {plan.name}: {e}")
            continue
    
    print(f"\n🎉 PRODUCTION SETUP COMPLETE!")
    print("=" * 50)
    
    if created_products:
        print(f"✅ Successfully created {len(created_products)} products:")
        for item in created_products:
            plan = item['plan']
            print(f"   • {plan.name}")
            print(f"     Product: {item['product_id']}")
            print(f"     Price: {item['price_id']}")
            print(f"     Amount: ${plan.price}/{plan.billing_period}")
        
        print(f"\n📋 NEXT STEPS:")
        print("1. Set up webhook endpoint in Stripe Dashboard:")
        print("   https://dashboard.stripe.com/webhooks")
        print("2. Add endpoint URL: https://yourdomain.com/subscriptions/webhook/")
        print("3. Select events: checkout.session.completed, invoice.payment_succeeded")
        print("4. Copy webhook signing secret to production .env")
        print("5. Test with small real payment")
        
        return True
    else:
        print("❌ No products were created successfully")
        return False

def verify_production_setup():
    """Verify all plans have live Stripe IDs."""
    print(f"\n🔍 VERIFYING PRODUCTION SETUP")
    print("=" * 50)
    
    plans = SubscriptionPlan.objects.filter(is_active=True)
    missing_stripe_ids = []
    
    for plan in plans:
        if not plan.stripe_price_id or not plan.stripe_product_id:
            missing_stripe_ids.append(plan)
        else:
            print(f"✅ {plan.name}")
            print(f"   Product: {plan.stripe_product_id}")
            print(f"   Price: {plan.stripe_price_id}")
    
    if missing_stripe_ids:
        print(f"\n⚠️  Warning: {len(missing_stripe_ids)} plans missing Stripe IDs:")
        for plan in missing_stripe_ids:
            print(f"   - {plan.name}")
        return False
    
    print(f"\n✅ All {plans.count()} plans have live Stripe IDs!")
    return True

if __name__ == '__main__':
    print("🏭 STRIPE PRODUCTION SETUP")
    print("=" * 50)
    print("This script creates LIVE Stripe products for production use.")
    print("Only run this on your production server!")
    
    if create_production_stripe_products():
        verify_production_setup()
        print(f"\n🚀 PRODUCTION STRIPE SETUP SUCCESSFUL!")
        print("Your payment system is ready for live customers!")
    else:
        print(f"\n❌ PRODUCTION SETUP FAILED")
        print("Please check errors and try again.")
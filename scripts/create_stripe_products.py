#!/usr/bin/env python
"""
Script to create Stripe products and prices for production.
Run this in production environment with live Stripe keys.
"""

import os
import sys
import django
import stripe

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.production')
django.setup()

from django.conf import settings
from subscriptions.models import SubscriptionPlan

def create_stripe_products():
    """Create products and prices in Stripe for production."""
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    print("🏭 CREATING STRIPE PRODUCTS FOR PRODUCTION")
    print("=" * 60)
    
    plans = SubscriptionPlan.objects.filter(is_active=True)
    
    for plan in plans:
        print(f"\n📦 Creating product for: {plan.name}")
        
        try:
            # Create product
            product = stripe.Product.create(
                name=plan.name,
                description=plan.description,
                metadata={
                    'plan_id': str(plan.id),
                    'plan_type': plan.plan_type,
                    'assessment_credits': str(plan.assessment_credits),
                }
            )
            
            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=int(plan.price * 100),  # Convert to cents
                currency=plan.currency.lower(),
                recurring={
                    'interval': 'month' if plan.billing_period == 'monthly' else 'year',
                    'interval_count': 1 if plan.billing_period == 'monthly' else 12 if plan.billing_period == 'annual' else 3
                },
                metadata={
                    'plan_id': str(plan.id),
                    'billing_period': plan.billing_period,
                }
            )
            
            # Update local plan with Stripe IDs
            plan.stripe_product_id = product.id
            plan.stripe_price_id = price.id
            plan.save()
            
            print(f"✅ Created product: {product.id}")
            print(f"✅ Created price: {price.id}")
            print(f"✅ Updated local plan with Stripe IDs")
            
        except Exception as e:
            print(f"❌ Error creating product for {plan.name}: {e}")
    
    print(f"\n🎉 PRODUCTION STRIPE SETUP COMPLETE!")
    print("Next steps:")
    print("1. Update your production environment with live Stripe keys")
    print("2. Set up webhook endpoint in Stripe dashboard")
    print("3. Test with live payment cards")

if __name__ == '__main__':
    create_stripe_products()
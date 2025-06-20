#!/usr/bin/env python
"""
Test subscription dashboard access to verify timezone fixes.
"""

import os
import sys
import django

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from subscriptions.models import UserSubscription
from subscriptions.services import stripe_service

def test_subscription_dashboard():
    """Test that subscription dashboard can be accessed without errors."""
    User = get_user_model()
    
    try:
        # Get user with subscription
        user = User.objects.get(id=1)
        subscription = getattr(user, 'subscription', None)
        
        if not subscription:
            print("❌ No subscription found for user")
            return False
            
        print(f"✅ Found subscription: {subscription.id}")
        print(f"   Status: {subscription.status}")
        print(f"   Plan: {subscription.plan.name}")
        print(f"   Stripe ID: {subscription.stripe_subscription_id}")
        
        # Test sync_subscription_status method (this was failing with timezone errors)
        print("\n🧪 Testing sync_subscription_status method...")
        updated_subscription = stripe_service.sync_subscription_status(subscription)
        
        print(f"✅ Sync successful!")
        print(f"   Status: {updated_subscription.status}")
        print(f"   Current period: {updated_subscription.current_period_start} to {updated_subscription.current_period_end}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Testing subscription dashboard access...")
    success = test_subscription_dashboard()
    
    if success:
        print("\n🎉 Subscription dashboard should now work without timezone errors!")
    else:
        print("\n💥 Still has errors - needs further investigation")
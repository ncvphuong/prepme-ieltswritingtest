#!/usr/bin/env python
"""
Debug webhook configuration and test locally.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
django.setup()

from django.conf import settings

def check_webhook_config():
    """Check webhook configuration."""
    print("🔍 WEBHOOK CONFIGURATION DEBUG")
    print("=" * 50)
    
    print(f"STRIPE_WEBHOOK_SECRET: {settings.STRIPE_WEBHOOK_SECRET[:20]}...")
    print(f"Length: {len(settings.STRIPE_WEBHOOK_SECRET)}")
    print(f"Starts with 'whsec_': {settings.STRIPE_WEBHOOK_SECRET.startswith('whsec_')}")
    
    print("\n📋 WEBHOOK SETUP INSTRUCTIONS:")
    print("1. Stop current Stripe CLI listener (Ctrl+C)")
    print("2. Your webhook secret is:", settings.STRIPE_WEBHOOK_SECRET)
    print("3. Start fresh Stripe CLI listener:")
    print("   stripe listen --forward-to localhost:8000/subscriptions/webhook/")
    print("4. Copy the new webhook secret (whsec_xxx) from CLI output")
    print("5. Update your .env file with the new secret")
    print("6. Restart Django server")
    
    print("\n🧪 ALTERNATIVE: Test with actual webhook secret")
    print("If you want to use your current secret, restart Stripe CLI with:")
    print("stripe listen --forward-to localhost:8000/subscriptions/webhook/")
    print("And use the signing secret it provides")

if __name__ == '__main__':
    check_webhook_config()
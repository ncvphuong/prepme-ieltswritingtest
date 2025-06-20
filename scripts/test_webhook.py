#!/usr/bin/env python
"""
Test webhook endpoint locally.
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
django.setup()

def test_webhook_endpoint():
    """Test that the webhook endpoint is accessible."""
    webhook_url = "http://localhost:8000/subscriptions/webhook/"
    
    print(f"🧪 Testing webhook endpoint: {webhook_url}")
    
    # Test simple GET request (should return 405 Method Not Allowed)
    try:
        response = requests.get(webhook_url, timeout=5)
        print(f"✅ Webhook endpoint is accessible (GET returned {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server. Make sure it's running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ Error testing webhook endpoint: {e}")
        return False

def test_webhook_logs():
    """Check if webhook processing is working."""
    print("\n📋 WEBHOOK DEBUGGING CHECKLIST:")
    print("1. Is Django server running on port 8000?")
    print("2. Is Stripe CLI listening with: stripe listen --forward-to localhost:8000/subscriptions/webhook/")
    print("3. Check Django terminal for webhook log messages")
    print("4. Your webhook secret should be: whsec_WcbwD6njL7iYVUq2MfsvEuTp8gN0NSs7")
    
    # Test the webhook URL pattern
    from django.urls import reverse
    try:
        webhook_path = reverse('subscriptions:stripe_webhook')
        print(f"✅ Webhook URL pattern is correct: {webhook_path}")
    except Exception as e:
        print(f"❌ Webhook URL pattern error: {e}")

def main():
    """Run webhook tests."""
    print("🎣 WEBHOOK TESTING SUITE")
    print("=" * 40)
    
    if test_webhook_endpoint():
        test_webhook_logs()
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Make sure Django is running: python manage.py runserver 8000")
        print("2. Start Stripe CLI: stripe listen --forward-to localhost:8000/subscriptions/webhook/")
        print("3. Test payment: stripe trigger checkout.session.completed")
        print("4. Watch Django terminal for webhook processing logs")
        print("5. Check Stripe dashboard for event delivery status")
    else:
        print("❌ Fix Django server connection first")

if __name__ == '__main__':
    main()
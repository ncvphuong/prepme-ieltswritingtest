#!/usr/bin/env python
"""
Direct fix for Stripe key loading issue.
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_direct_env_loading():
    """Test loading .env file directly."""
    
    # Read .env file directly
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        
        print("🔍 DIRECT .env FILE READING:")
        print("=" * 50)
        for key in ['STRIPE_SECRET_KEY', 'STRIPE_PUBLIC_KEY', 'STRIPE_WEBHOOK_SECRET']:
            if key in env_vars:
                value = env_vars[key]
                print(f"{key}: {value[:20]}... (length: {len(value)})")
        
        # Test with these values
        if 'STRIPE_SECRET_KEY' in env_vars:
            stripe_key = env_vars['STRIPE_SECRET_KEY']
            if len(stripe_key) > 100:
                print("✅ Found valid Stripe secret key!")
                
                # Set environment variables directly
                os.environ['STRIPE_SECRET_KEY'] = stripe_key
                os.environ['STRIPE_PUBLIC_KEY'] = env_vars.get('STRIPE_PUBLIC_KEY', '')
                os.environ['STRIPE_WEBHOOK_SECRET'] = env_vars.get('STRIPE_WEBHOOK_SECRET', '')
                
                print("✅ Environment variables set directly!")
                return True
            else:
                print("❌ Stripe key too short")
                return False
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def test_stripe_connection():
    """Test Stripe connection with direct environment variables."""
    
    # Setup Django with direct env vars
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
    import django
    django.setup()
    
    from django.conf import settings
    import stripe
    
    print("\n🧪 TESTING STRIPE CONNECTION:")
    print("=" * 50)
    
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        print(f"Using key: {settings.STRIPE_SECRET_KEY[:20]}... (length: {len(settings.STRIPE_SECRET_KEY)})")
        
        # Test basic API call
        customers = stripe.Customer.list(limit=1)
        print("✅ Stripe API connection successful!")
        return True
        
    except stripe.error.AuthenticationError as e:
        print(f"❌ Stripe authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Stripe connection error: {e}")
        return False

def main():
    """Main function."""
    if test_direct_env_loading():
        test_stripe_connection()
    else:
        print("❌ Could not load valid Stripe keys from .env file")
        print("\n💡 MANUAL SOLUTION:")
        print("1. Open your .env file in a text editor")
        print("2. Verify your STRIPE_SECRET_KEY is set correctly with your actual Stripe test key")
        print("3. Ensure the key starts with 'sk_test_' for test mode")
        print("4. Save the file and restart Django")

if __name__ == '__main__':
    main()
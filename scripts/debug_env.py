#!/usr/bin/env python
"""
Debug environment variables loading.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_env_file():
    """Check .env file content."""
    print("🔍 CHECKING .env FILE")
    print("=" * 40)
    
    env_path = Path('.env')
    if env_path.exists():
        print(f"✅ .env file found at: {env_path.absolute()}")
        with open(env_path, 'r') as f:
            content = f.read()
            
        # Check for Stripe keys
        lines = content.split('\n')
        for line in lines:
            if 'STRIPE_SECRET_KEY' in line:
                key_part = line.split('=')[1] if '=' in line else 'NOT_FOUND'
                print(f"STRIPE_SECRET_KEY: {key_part[:20]}... (length: {len(key_part)})")
            elif 'STRIPE_PUBLIC_KEY' in line:
                key_part = line.split('=')[1] if '=' in line else 'NOT_FOUND'
                print(f"STRIPE_PUBLIC_KEY: {key_part[:20]}... (length: {len(key_part)})")
            elif 'STRIPE_WEBHOOK_SECRET' in line:
                key_part = line.split('=')[1] if '=' in line else 'NOT_FOUND'
                print(f"STRIPE_WEBHOOK_SECRET: {key_part[:20]}... (length: {len(key_part)})")
    else:
        print("❌ .env file not found!")

def check_django_settings():
    """Check Django settings loading."""
    print("\n🔍 CHECKING DJANGO SETTINGS")
    print("=" * 40)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.development')
        import django
        django.setup()
        
        from django.conf import settings
        
        print(f"STRIPE_SECRET_KEY in Django: {settings.STRIPE_SECRET_KEY[:20]}... (length: {len(settings.STRIPE_SECRET_KEY)})")
        print(f"STRIPE_PUBLIC_KEY in Django: {settings.STRIPE_PUBLIC_KEY[:20]}... (length: {len(settings.STRIPE_PUBLIC_KEY)})")
        print(f"STRIPE_WEBHOOK_SECRET in Django: {settings.STRIPE_WEBHOOK_SECRET[:20]}... (length: {len(settings.STRIPE_WEBHOOK_SECRET)})")
        
        # Check if they're real keys
        print(f"Secret key starts with 'sk_test_': {settings.STRIPE_SECRET_KEY.startswith('sk_test_')}")
        print(f"Public key starts with 'pk_test_': {settings.STRIPE_PUBLIC_KEY.startswith('pk_test_')}")
        print(f"Webhook secret starts with 'whsec_': {settings.STRIPE_WEBHOOK_SECRET.startswith('whsec_')}")
        
    except Exception as e:
        print(f"❌ Error loading Django settings: {e}")

def check_decouple():
    """Check python-decouple directly."""
    print("\n🔍 CHECKING PYTHON-DECOUPLE")
    print("=" * 40)
    
    try:
        from decouple import config
        
        stripe_secret = config('STRIPE_SECRET_KEY', default='NOT_FOUND')
        stripe_public = config('STRIPE_PUBLIC_KEY', default='NOT_FOUND')
        stripe_webhook = config('STRIPE_WEBHOOK_SECRET', default='NOT_FOUND')
        
        print(f"Decouple STRIPE_SECRET_KEY: {stripe_secret[:20]}... (length: {len(stripe_secret)})")
        print(f"Decouple STRIPE_PUBLIC_KEY: {stripe_public[:20]}... (length: {len(stripe_public)})")
        print(f"Decouple STRIPE_WEBHOOK_SECRET: {stripe_webhook[:20]}... (length: {len(stripe_webhook)})")
        
    except Exception as e:
        print(f"❌ Error with python-decouple: {e}")

def main():
    """Run all checks."""
    check_env_file()
    check_decouple()
    check_django_settings()
    
    print("\n💡 SOLUTION:")
    print("1. If keys are showing as placeholders, restart Django server")
    print("2. Make sure .env file has no extra spaces or characters")
    print("3. Verify STRIPE_SECRET_KEY starts with 'sk_test_' and is ~108 characters")
    print("4. Check that there are no duplicate entries in .env file")

if __name__ == '__main__':
    main()
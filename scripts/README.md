# Scripts Directory

This directory contains helper scripts for managing the IELTS Writing Test platform.

## 🏭 **Production Setup Scripts**

### `setup_production_stripe.py`
**🚨 PRODUCTION ONLY** - Creates live Stripe products and prices
```bash
# On production server only
python scripts/setup_production_stripe.py
```

## 🧪 **Development & Testing Scripts**

### `setup_stripe_test_products.py`
Creates test Stripe products for development
```bash
python scripts/setup_stripe_test_products.py
```

### `create_plans.py`
Creates initial subscription plans in Django database
```bash
python scripts/create_plans.py
```

### `test_stripe_integration.py`
Tests Stripe integration and displays test instructions
```bash
python scripts/test_stripe_integration.py
```

## 🔧 **Debug & Troubleshooting Scripts**

### `debug_env.py`
Debugs environment variable loading issues
```bash
python scripts/debug_env.py
```

### `debug_webhook.py`
Debugs webhook configuration
```bash
python scripts/debug_webhook.py
```

### `test_webhook.py`
Tests webhook endpoint connectivity
```bash
python scripts/test_webhook.py
```

### `fix_stripe_keys.py`
Fixes Stripe key loading issues (bypasses decouple cache)
```bash
python scripts/fix_stripe_keys.py
```

## 📦 **Legacy Scripts**

### `create_stripe_products.py`
Original script for creating Stripe products (superseded by setup_stripe_test_products.py)

## 🚀 **Usage Examples**

### **Initial Development Setup**
```bash
# 1. Create subscription plans
python scripts/create_plans.py

# 2. Create test Stripe products
python scripts/setup_stripe_test_products.py

# 3. Test integration
python scripts/test_stripe_integration.py
```

### **Production Deployment**
```bash
# 1. Ensure plans exist
python scripts/create_plans.py

# 2. Create LIVE Stripe products (production server only!)
python scripts/setup_production_stripe.py
```

### **Troubleshooting**
```bash
# Debug environment variables
python scripts/debug_env.py

# Debug webhook setup
python scripts/debug_webhook.py

# Test webhook connectivity
python scripts/test_webhook.py
```

## ⚠️ **Important Notes**

- **Production scripts**: Only run `setup_production_stripe.py` on production with live Stripe keys
- **Environment**: All scripts automatically detect and use appropriate Django settings
- **Safety**: Production scripts include verification and confirmation steps
- **Logging**: All scripts provide detailed output for debugging

## 📋 **Script Dependencies**

All scripts require:
- Django environment properly configured
- Required packages installed (`stripe`, `django`, etc.)
- Appropriate environment variables set (.env file)

For production scripts, additionally require:
- `DEBUG=False`
- Live Stripe keys (`sk_live_`, `pk_live_`)
- Production database access
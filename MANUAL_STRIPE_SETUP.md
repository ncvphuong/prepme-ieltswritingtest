# Manual Stripe Production Setup Guide

If you prefer to create products manually in the Stripe Dashboard, follow these exact steps:

## 🏭 **Step 1: Switch to Live Mode**

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Toggle from "Test mode" to "Live mode" (top right)
3. Ensure you see "Live mode" indicator

## 📦 **Step 2: Create Products**

Go to **Products** → **Add Product** and create these 3 products:

### **Product 1: Basic Monthly**
- **Name**: `Basic Monthly`
- **Description**: `Perfect for getting started with IELTS writing practice`
- **Pricing Model**: `Recurring`
- **Price**: `$19.99`
- **Billing Period**: `Monthly`
- **Currency**: `USD`

**Metadata** (Advanced settings):
```
plan_type: basic
assessment_credits: 20
environment: production
```

### **Product 2: Premium Monthly** 
- **Name**: `Premium Monthly`
- **Description**: `Most popular plan with comprehensive features`
- **Pricing Model**: `Recurring`
- **Price**: `$39.99`
- **Billing Period**: `Monthly`
- **Currency**: `USD`

**Metadata**:
```
plan_type: premium
assessment_credits: 50
environment: production
```

### **Product 3: Pro Annual**
- **Name**: `Pro Annual`
- **Description**: `Best value for serious IELTS candidates`
- **Pricing Model**: `Recurring`
- **Price**: `$399.99`
- **Billing Period**: `Yearly`
- **Currency**: `USD`

**Metadata**:
```
plan_type: pro
assessment_credits: 100
environment: production
```

## 🔗 **Step 3: Update Django Database**

After creating products in Stripe, you need to update your Django database with the price IDs:

1. Copy the **Price ID** from each product (starts with `price_`)
2. Run this script on your production server:

```python
# update_stripe_ids.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ieltswritingtest.settings.production')
django.setup()

from subscriptions.models import SubscriptionPlan

# Update with your actual Stripe Price IDs from the dashboard
STRIPE_PRICE_IDS = {
    'Basic Monthly': 'price_1XXXXXXbasic_monthly_live',      # Replace with real ID
    'Premium Monthly': 'price_1XXXXXXpremium_monthly_live',   # Replace with real ID
    'Pro Annual': 'price_1XXXXXXpro_annual_live',            # Replace with real ID
}

STRIPE_PRODUCT_IDS = {
    'Basic Monthly': 'prod_XXXXXXbasic_live',      # Replace with real ID
    'Premium Monthly': 'prod_XXXXXXpremium_live',   # Replace with real ID
    'Pro Annual': 'prod_XXXXXXpro_live',           # Replace with real ID
}

for plan_name, price_id in STRIPE_PRICE_IDS.items():
    try:
        plan = SubscriptionPlan.objects.get(name=plan_name)
        plan.stripe_price_id = price_id
        plan.stripe_product_id = STRIPE_PRODUCT_IDS[plan_name]
        plan.save()
        print(f"✅ Updated {plan_name}: {price_id}")
    except SubscriptionPlan.DoesNotExist:
        print(f"❌ Plan not found: {plan_name}")

print("🎉 Database updated with live Stripe IDs!")
```

## 🎣 **Step 4: Set Up Webhook**

1. Go to **Developers** → **Webhooks** → **Add endpoint**
2. **Endpoint URL**: `https://yourdomain.com/subscriptions/webhook/`
3. **Events to send**:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. **Copy the signing secret** (starts with `whsec_`)
5. **Add to production .env**:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret
   ```

## ✅ **Step 5: Test Live Payment**

⚠️ **Use a real card with a small amount first!**

1. Visit your production site
2. Subscribe to Basic Monthly ($19.99)
3. Use a real credit card
4. Verify:
   - Payment succeeds in Stripe
   - Webhook processes correctly
   - User subscription created in database
   - Credits assigned properly

## 🔍 **Verification Checklist**

- [ ] 3 products created in Stripe Live mode
- [ ] All products have correct pricing and intervals
- [ ] Django database updated with live price IDs
- [ ] Webhook endpoint configured
- [ ] Webhook secret added to production .env
- [ ] Test payment completed successfully
- [ ] Webhook events processing correctly

---

**Live Price ID Format Examples:**
- Basic: `price_1Rc2NGRwssazqmBmXXXXXX`
- Premium: `price_1Rc2NHRwssazqmBmYYYYYY`
- Pro: `price_1Rc2NHRwssazqmBmZZZZZZ`

Copy the exact IDs from your Stripe Dashboard!
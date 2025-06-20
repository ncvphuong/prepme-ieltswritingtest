"""
Admin interface for subscription models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import SubscriptionPlan, UserSubscription, PaymentHistory, UsageRecord


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'plan_type', 'billing_period', 'price', 'currency',
        'assessment_credits', 'is_active', 'is_featured', 'sort_order'
    ]
    list_filter = ['plan_type', 'billing_period', 'is_active', 'is_featured']
    list_editable = ['is_active', 'is_featured', 'sort_order']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'plan_type', 'billing_period', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'currency')
        }),
        ('Features', {
            'fields': (
                'assessment_credits', 'practice_tasks_limit',
                'priority_support', 'advanced_analytics', 'features'
            )
        }),
        ('Stripe Integration', {
            'fields': ('stripe_price_id', 'stripe_product_id'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'is_featured', 'sort_order')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ['slug']
        return []


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'plan', 'status', 'current_period_end',
        'assessment_credits_remaining', 'assessment_credits_used',
        'is_active', 'cancel_at_period_end'
    ]
    list_filter = [
        'status', 'plan__plan_type', 'cancel_at_period_end',
        'current_period_start', 'current_period_end'
    ]
    search_fields = ['user__username', 'user__email', 'plan__name']
    readonly_fields = [
        'stripe_subscription_id', 'stripe_customer_id',
        'created_at', 'updated_at', 'is_active', 'is_trial', 'days_remaining'
    ]
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Billing Period', {
            'fields': (
                'current_period_start', 'current_period_end',
                'trial_end', 'is_active', 'days_remaining'
            )
        }),
        ('Usage Tracking', {
            'fields': (
                'assessment_credits_used', 'assessment_credits_remaining'
            )
        }),
        ('Stripe Integration', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('cancel_at_period_end', 'canceled_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'
    
    def is_trial(self, obj):
        return obj.is_trial
    is_trial.boolean = True
    is_trial.short_description = 'Trial'
    
    def days_remaining(self, obj):
        days = obj.days_remaining
        if days > 0:
            return f"{days} days"
        return "Expired"
    days_remaining.short_description = 'Days Left'


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'plan', 'amount', 'currency',
        'status', 'payment_method', 'created_at'
    ]
    list_filter = [
        'status', 'currency', 'plan__plan_type',
        'created_at', 'period_start', 'period_end'
    ]
    search_fields = [
        'user__username', 'user__email', 'plan__name',
        'stripe_payment_intent_id', 'stripe_invoice_id'
    ]
    readonly_fields = [
        'stripe_payment_intent_id', 'stripe_invoice_id',
        'created_at', 'updated_at'
    ]
    raw_id_fields = ['user', 'subscription']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('user', 'subscription', 'plan', 'amount', 'currency', 'status')
        }),
        ('Payment Method', {
            'fields': ('payment_method', 'failure_reason')
        }),
        ('Billing Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_payment_intent_id', 'stripe_invoice_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Payment records should only be created via Stripe webhooks
        return False


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'usage_type', 'quantity', 'description',
        'billable', 'billed_at', 'created_at'
    ]
    list_filter = [
        'usage_type', 'billable', 'created_at',
        'subscription__plan__plan_type'
    ]
    search_fields = [
        'user__username', 'user__email', 'description',
        'metadata'
    ]
    readonly_fields = ['created_at', 'updated_at', 'formatted_metadata']
    raw_id_fields = ['user', 'subscription']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Usage Details', {
            'fields': ('user', 'subscription', 'usage_type', 'quantity', 'description')
        }),
        ('Billing', {
            'fields': ('billable', 'billed_at')
        }),
        ('Metadata', {
            'fields': ('formatted_metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_metadata(self, obj):
        if obj.metadata:
            formatted = json.dumps(obj.metadata, indent=2)
            return format_html('<pre>{}</pre>', formatted)
        return '-'
    formatted_metadata.short_description = 'Metadata (JSON)'
    
    def has_add_permission(self, request):
        # Usage records should only be created programmatically
        return False


# Customize admin site header
admin.site.site_header = 'IELTS Writing Test Admin'
admin.site.site_title = 'IELTS Admin'
admin.site.index_title = 'Welcome to IELTS Writing Test Administration'

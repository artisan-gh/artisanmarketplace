from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price', 'currency', 'billing_cycle',
        'duration_days', 'is_active', 'trial_days', 'created_at'
    )
    list_filter = ('is_active', 'billing_cycle', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('price',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'subscription_reference', 'user', 'plan', 'start_date',
        'end_date', 'status', 'auto_renew', 'created_at'
    )
    list_filter = ('status', 'auto_renew', 'created_at')
    search_fields = ('subscription_reference', 'user__email', 'plan__name')
    readonly_fields = ('subscription_reference', 'created_at', 'updated_at', 'cancelled_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Subscription', {'fields': ('subscription_reference', 'user', 'plan')}),
        ('Dates', {'fields': ('start_date', 'end_date', 'trial_end_date', 'cancelled_at')}),
        ('Status', {'fields': ('status', 'auto_renew')}),
        ('Payment', {'fields': ('gateway_reference', 'gateway_response')}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

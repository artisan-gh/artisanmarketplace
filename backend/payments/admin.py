from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_reference',
        'user',
        'amount',
        'currency',
        'status',
        'payment_method',
        'paid_at',
        'is_successful',
        'created_at',
    )
    list_filter = ('status', 'payment_method', 'currency', 'created_at')
    search_fields = ('transaction_reference', 'gateway_reference', 'user__email')
    readonly_fields = (
        'transaction_reference', 'net_amount', 'created_at', 'updated_at',
        'refunded_amount', 'refund_reference', 'refunded_at'
    )
    ordering = ('-created_at',)
    raw_id_fields = ('user',)

    fieldsets = (
        ('Transaction', {'fields': ('transaction_reference', 'gateway_reference', 'user')}),
        ('Financial', {'fields': ('amount', 'currency', 'fee', 'net_amount')}),
        ('Status', {'fields': ('status', 'payment_method', 'paid_at')}),
        ('Refund', {'fields': ('refunded_amount', 'refund_reference', 'refunded_at', 'refund_reason')}),
        ('Details', {'fields': ('description', 'notes', 'gateway_response')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def is_successful(self, obj):
        return obj.is_successful
    is_successful.boolean = True
    is_successful.short_description = 'Successful?'

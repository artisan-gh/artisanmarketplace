from django.contrib import admin
from .models import Wallet, WalletTransaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'balance',
        'currency',
        'total_earned',
        'total_withdrawn',
        'is_active',
        'last_transaction_at',
        'created_at',
    )
    list_filter = ('is_active', 'currency', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('balance', 'total_earned', 'total_withdrawn', 'last_transaction_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Balance', {'fields': ('balance', 'currency', 'total_earned', 'total_withdrawn')}),
        ('Status', {'fields': ('is_active', 'last_transaction_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'wallet',
        'transaction_type',
        'amount',
        'balance_after',
        'status',
        'created_at',
    )
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference', 'description', 'wallet__user__email')
    readonly_fields = ('reference', 'balance_after', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Wallet', {'fields': ('wallet',)}),
        ('Transaction', {'fields': ('reference', 'transaction_type', 'amount', 'description', 'balance_after')}),
        ('Status', {'fields': ('status', 'processed_at')}),
        ('Metadata', {'fields': ('metadata',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

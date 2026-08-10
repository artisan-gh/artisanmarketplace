# billing/admin.py
from django.contrib import admin
from .models import (
    Invoice, InvoiceItem, InvoiceItemTax, BillingConfig,
    Payment, PaymentAllocation, CreditNote, InvoiceApproval,
    InvoiceHistory, InvoiceTag, InvoiceComment, InvoiceAttachment,
    RecurringInvoice, LedgerAccount, JournalEntry, JournalEntryLine,
    PaymentIntent, PaymentGatewayTransaction, WebhookLog,
    PaymentDueReminder, CustomerStatement, CustomerStatementLine,
    InvoiceSequence, ExchangeRate, Tax, InvoiceTemplate,
    PurchasedItem
)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'sku', 'unit', 'quantity', 'unit_price', 'discount_percent', 'line_total']
    readonly_fields = ['line_total']


class PurchasedItemInline(admin.TabularInline):
    model = PurchasedItem
    extra = 1
    fields = ['description', 'quantity', 'unit_cost', 'total_cost']
    readonly_fields = ['total_cost']


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 1
    fields = ['invoice', 'amount']
    raw_id_fields = ['invoice']


class InvoiceApprovalInline(admin.TabularInline):
    model = InvoiceApproval
    extra = 0
    fields = ['level', 'approver', 'status', 'comments', 'approved_at']
    readonly_fields = ['approved_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'customer', 'grand_total', 'currency',
        'status', 'issued_date', 'due_date', 'is_overdue', 'is_paid',
        'paystack_reference_display', 'amount_in_smallest_unit_display',
        'transport_cost'  # <-- added
    ]
    list_filter = ['status', 'invoice_type', 'currency', 'issued_date', 'due_date', 'is_deleted']
    search_fields = [
        'invoice_number', 'customer__name', 'customer__email',
        'paystack_reference'
    ]
    readonly_fields = [
        'invoice_number', 'public_token', 'subtotal', 'tax_amount',
        'discount_amount', 'grand_total', 'amount_paid', 'balance_due',
        'materials_total',
        'transport_cost',  # <-- added
        'converted_total',
        'version', 'created_at', 'updated_at', 'deleted_at',
        'paystack_reference', 'paystack_access_code',
        'amount_in_smallest_unit_display'
    ]
    raw_id_fields = ['customer', 'incident', 'created_by', 'email_sent_by', 'organization']
    inlines = [
        InvoiceItemInline,
        PurchasedItemInline,
        PaymentAllocationInline,
        InvoiceApprovalInline
    ]
    fieldsets = (
        (None, {
            'fields': ('invoice_number', 'public_token', 'status', 'invoice_type')
        }),
        ('Customer', {
            'fields': ('customer', 'billing_name', 'billing_address', 'billing_phone', 'billing_email', 'billing_tax_id')
        }),
        ('Dates', {
            'fields': ('issued_date', 'due_date', 'paid_date', 'approved_at', 'pdf_generated_at', 'emailed_at')
        }),
        ('Financial', {
            'fields': (
                'subtotal', 'tax_amount', 'discount_amount',
                'materials_total',
                'transport_cost',  # <-- added
                'grand_total', 'amount_paid', 'balance_due', 'currency'
            )
        }),
        ('Exchange', {
            'fields': ('exchange_rate', 'base_currency', 'converted_total')
        }),
        ('Paystack', {
            'fields': ('paystack_reference', 'paystack_access_code', 'amount_in_smallest_unit_display'),
            'classes': ('collapse',)
        }),
        ('Other', {
            'fields': ('notes', 'terms', 'tags', 'pdf_file', 'version')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'deleted_at', 'created_by', 'email_sent_by'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Paystack Reference', ordering='paystack_reference')
    def paystack_reference_display(self, obj):
        return obj.paystack_reference or '—'

    @admin.display(description='Amount (Smallest Unit)', ordering='grand_total')
    def amount_in_smallest_unit_display(self, obj):
        if obj.grand_total:
            return f"{obj.amount_in_smallest_unit} {obj.currency} (smallest unit)"
        return '—'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'amount', 'currency', 'method', 'status', 'paid_at'
    ]
    list_filter = ['status', 'method', 'currency', 'paid_at']
    search_fields = ['customer__name', 'gateway_reference']
    readonly_fields = ['net_amount', 'created_at', 'updated_at']
    raw_id_fields = ['customer']
    inlines = [PaymentAllocationInline]


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ['credit_number', 'invoice', 'amount', 'currency', 'status', 'issued_date']
    list_filter = ['status', 'currency', 'issued_date']
    search_fields = ['credit_number', 'invoice__invoice_number', 'reason']
    raw_id_fields = ['invoice', 'payment', 'created_by']


@admin.register(InvoiceHistory)
class InvoiceHistoryAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'action', 'user', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['invoice__invoice_number', 'user__email']
    raw_id_fields = ['invoice', 'user']
    readonly_fields = (
        'invoice', 'action', 'user', 'reason', 'old_status',
        'new_status', 'metadata', 'created_at'
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BillingConfig)
class BillingConfigAdmin(admin.ModelAdmin):
    list_display = ['currency', 'default_tax_rate', 'is_active']
    list_filter = ['is_active', 'currency']


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_type', 'rate', 'is_active', 'effective_from']
    list_filter = ['tax_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(InvoiceTag)
class InvoiceTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']


@admin.register(RecurringInvoice)
class RecurringInvoiceAdmin(admin.ModelAdmin):
    list_display = ['customer', 'frequency', 'next_issue_date', 'is_active']
    list_filter = ['frequency', 'is_active']


@admin.register(LedgerAccount)
class LedgerAccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['code', 'name']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'description', 'posted_at']
    search_fields = ['entry_number', 'description']
    readonly_fields = ['entry_number', 'posted_at']


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'amount', 'gateway_reference', 'status', 'expires_at']
    list_filter = ['status', 'gateway']


@admin.register(InvoiceAttachment)
class InvoiceAttachmentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'filename', 'uploaded_by', 'created_at']


@admin.register(InvoiceComment)
class InvoiceCommentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'user', 'is_internal', 'created_at']


@admin.register(InvoiceApproval)
class InvoiceApprovalAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'level', 'approver', 'status']
    list_filter = ['level', 'status']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['base_currency', 'target_currency', 'rate', 'effective_date']
    list_filter = ['base_currency', 'target_currency']


@admin.register(InvoiceSequence)
class InvoiceSequenceAdmin(admin.ModelAdmin):
    list_display = ['prefix', 'year', 'current_number']


@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'is_default']
    list_filter = ['is_default']
    search_fields = ['name']


@admin.register(PurchasedItem)
class PurchasedItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_cost', 'total_cost']
    list_filter = ['invoice__status']
    search_fields = ['description', 'invoice__invoice_number']
    raw_id_fields = ['invoice']
    readonly_fields = ['total_cost']

from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ('total',)
    fields = ('description', 'quantity', 'unit_price', 'total')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'client',
        'total',
        'currency',
        'status',
        'issued_date',
        'due_date',
        'created_at'
    )
    list_filter = ('status', 'issued_date', 'due_date', 'created_at')
    search_fields = ('invoice_number', 'client__email', 'client__first_name', 'client__last_name')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at', 'sent_date', 'paid_date', 'tax_amount')
    ordering = ('-created_at',)
    inlines = [InvoiceItemInline]
    raw_id_fields = ('client', 'payment')

    fieldsets = (
        ('Invoice Info', {'fields': ('invoice_number', 'client')}),
        ('Dates', {'fields': ('issued_date', 'due_date', 'sent_date', 'paid_date')}),
        ('Financial', {'fields': ('subtotal', 'tax_rate', 'tax_amount', 'discount', 'discount_type', 'total', 'currency')}),
        ('Status', {'fields': ('status', 'payment')}),
        ('Notes', {'fields': ('notes', 'terms')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'invoice', 'quantity', 'unit_price', 'total')
    list_filter = ('invoice',)
    search_fields = ('description',)

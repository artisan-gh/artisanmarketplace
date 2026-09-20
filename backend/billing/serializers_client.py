
from rest_framework import serializers
from .models import Invoice, InvoiceItem


class InvoiceItemClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ["description", "quantity", "unit_price",
                  "discount_amount", "tax_amount", "line_total"]
        read_only_fields = fields


class InvoiceClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "status", "currency",
                  "grand_total", "amount_paid", "balance_due",
                  "issued_date", "due_date", "paid_date", "public_token"]
        read_only_fields = fields


class InvoiceClientDetailSerializer(serializers.ModelSerializer):
    items = InvoiceItemClientSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "status", "currency",
                  "subtotal", "tax_amount", "discount_amount",
                  "materials_total", "transport_cost",
                  "grand_total", "amount_paid", "balance_due",
                  "issued_date", "due_date", "paid_date",
                  "billing_name", "billing_address", "billing_phone",
                  "notes", "terms", "items", "public_token"]
        read_only_fields = fields


class PublicInvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemClientSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Invoice
        fields = ["invoice_number", "status", "currency",
                  "subtotal", "tax_amount", "discount_amount",
                  "materials_total", "transport_cost",
                  "grand_total", "amount_paid", "balance_due",
                  "issued_date", "due_date", "paid_date",
                  "billing_name", "billing_address", "billing_phone",
                  "notes", "terms", "items", "customer_name"]
        read_only_fields = fields


class PublicInvoicePaySerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    channel = serializers.ChoiceField(
        choices=["card", "mobile_money", "bank_transfer"],
        required=False, allow_blank=True,
    )

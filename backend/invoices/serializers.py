from rest_framework import serializers
from .models import Invoice, InvoiceItem
# from bookings.serializers import BookingSerializer  # <-- REMOVED (bookings app deleted)
from payments.serializers import PaymentSerializer
from accounts.serializers import UserSerializer  # <-- Correct import


class InvoiceItemSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ('id', 'description', 'quantity', 'unit_price', 'total')
        # service removed – services app deleted
        read_only_fields = ('id',)


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    # booking_detail = BookingSerializer(source='booking', read_only=True)  # <-- COMMENTED OUT
    client_detail = UserSerializer(source='client', read_only=True)
    payment_detail = PaymentSerializer(source='payment', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = (
            'id', 'invoice_number', 'client', 'client_detail',
            # 'booking', 'booking_detail',  # <-- COMMENTED OUT
            'issued_date', 'due_date',
            'sent_date', 'paid_date', 'subtotal', 'tax_rate',
            'tax_amount', 'discount', 'discount_type', 'total',
            'currency', 'payment', 'payment_detail', 'status',
            'is_overdue', 'is_paid', 'notes', 'terms',
            'items', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'invoice_number', 'issued_date', 'tax_amount', 'total',
            'created_at', 'updated_at'
        )


class InvoiceListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    # booking_reference = serializers.CharField(source='booking.reference', read_only=True)  # <-- COMMENTED OUT

    class Meta:
        model = Invoice
        fields = (
            'id', 'invoice_number', 'client_name',
            # 'booking_reference',  # <-- COMMENTED OUT
            'total', 'currency', 'status', 'issued_date', 'due_date',
            'created_at'
        )


class InvoiceItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ('description', 'quantity', 'unit_price')
        # service removed – services app deleted


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemCreateSerializer(many=True)

    class Meta:
        model = Invoice
        fields = (
            'client',
            # 'booking',  # <-- COMMENTED OUT
            'due_date', 'subtotal',
            'tax_rate', 'discount', 'discount_type',
            'currency', 'notes', 'terms', 'items'
        )

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        invoice.calculate_totals()
        invoice.save()
        return invoice


class InvoiceSendSerializer(serializers.Serializer):
    send_email = serializers.BooleanField(default=False)
    email_body = serializers.CharField(required=False, allow_blank=True)
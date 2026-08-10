from rest_framework import serializers
from .models import Payment
# from bookings.serializers import BookingSerializer  # <-- REMOVED (bookings app deleted)


class PaymentSerializer(serializers.ModelSerializer):
    # booking_detail = BookingSerializer(source='booking', read_only=True)  # <-- COMMENTED OUT
    user_email = serializers.EmailField(source='user.email', read_only=True)
    refund_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    is_refunded = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id',
            'user',
            'user_email',
            # 'booking',          # <-- COMMENTED OUT (booking app deleted)
            # 'booking_detail',   # <-- COMMENTED OUT
            'transaction_reference',
            'gateway_reference',
            'amount',
            'currency',
            'fee',
            'net_amount',
            'status',
            'payment_method',
            'paid_at',
            'refunded_amount',
            'refund_reference',
            'refunded_at',
            'refund_reason',
            'refund_balance',
            'is_successful',
            'is_refunded',
            'description',
            'notes',
            'gateway_response',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'transaction_reference', 'gateway_reference', 'gateway_response',
            'status', 'paid_at', 'refunded_amount', 'refund_reference',
            'refunded_at', 'net_amount', 'created_at', 'updated_at'
        )


class PaymentListSerializer(serializers.ModelSerializer):
    # booking_title = serializers.CharField(source='booking.title', read_only=True)  # <-- COMMENTED OUT
    # client_name = serializers.CharField(source='booking.client.user.get_full_name', read_only=True)  # <-- COMMENTED OUT
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'transaction_reference', 'user_email',
            'amount', 'currency', 'status', 'payment_method', 'paid_at', 'created_at'
        )


class PaymentInitiateSerializer(serializers.Serializer):
    """
    Serializer for initiating a payment.
    """
    # booking_id = serializers.UUIDField(required=False)  # <-- COMMENTED OUT (booking app deleted)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=10, default='GHS')
    payment_method = serializers.ChoiceField(choices=Payment.PaymentMethod.choices, required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class PaymentRefundSerializer(serializers.Serializer):
    """
    Serializer for refunding a payment.
    """
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reason = serializers.CharField(required=False, allow_blank=True)


class PaymentWebhookSerializer(serializers.Serializer):
    """
    Serializer for payment gateway webhook payload.
    """
    transaction_reference = serializers.CharField()
    gateway_reference = serializers.CharField()
    status = serializers.ChoiceField(choices=Payment.PaymentStatus.choices)
    gateway_response = serializers.JSONField(required=False)


class WalletTopUpSerializer(serializers.Serializer):
    """
    Serializer for topping up a wallet.
    """
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)
    currency = serializers.CharField(max_length=10, default='GHS')
    description = serializers.CharField(required=False, allow_blank=True)   
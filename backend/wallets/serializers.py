from rest_framework import serializers
from .models import Wallet, WalletTransaction


# 1️⃣ Define WalletListSerializer first
class WalletListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Wallet
        fields = ('id', 'user_email', 'balance', 'currency', 'is_active', 'created_at')


# 2️⃣ Now define WalletTransactionSerializer – uses WalletListSerializer
class WalletTransactionSerializer(serializers.ModelSerializer):
    wallet = WalletListSerializer(read_only=True)  # ✅ now defined

    class Meta:
        model = WalletTransaction
        fields = (
            'id', 'reference', 'transaction_type', 'amount',
            'description', 'balance_after', 'status', 'processed_at',
            'metadata', 'created_at',
            'wallet',  # includes nested wallet with user_email
        )
        read_only_fields = ('reference', 'balance_after', 'status', 'processed_at', 'created_at')


# 3️⃣ WalletSerializer uses WalletTransactionSerializer
class WalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Wallet
        fields = (
            'id', 'user', 'user_email', 'balance', 'total_earned',
            'total_withdrawn', 'currency', 'is_active', 'last_transaction_at',
            'transactions', 'created_at', 'updated_at'
        )
        read_only_fields = ('balance', 'total_earned', 'total_withdrawn',
                           'last_transaction_at', 'created_at', 'updated_at')


# 4️⃣ Credit & Debit serializers (no changes)
class WalletCreditSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField()
    metadata = serializers.JSONField(required=False)


class WalletDebitSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField()
    metadata = serializers.JSONField(required=False)
from rest_framework import serializers
from .models import SubscriptionPlan, Subscription
from accounts.serializers import UserSerializer  # <-- fixed import


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = (
            'id', 'name', 'description', 'price', 'currency',
            'billing_cycle', 'duration_days', 'features',
            'is_active', 'trial_days', 'max_users', 'max_listings',
            'priority_support', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class SubscriptionPlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = (
            'id', 'name', 'price', 'currency', 'billing_cycle',
            'duration_days', 'is_active', 'trial_days'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    plan_detail = SubscriptionPlanSerializer(source='plan', read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    is_on_trial = serializers.BooleanField(read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'id', 'subscription_reference', 'user', 'user_detail',
            'plan', 'plan_detail', 'start_date', 'end_date',
            'trial_end_date', 'status', 'auto_renew', 'days_remaining',
            'is_on_trial', 'cancelled_at', 'gateway_reference',
            'gateway_response', 'notes', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'subscription_reference', 'status', 'cancelled_at',
            'gateway_response', 'created_at', 'updated_at'
        )


class SubscriptionListSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Subscription
        fields = (
            'id', 'subscription_reference', 'user_email',
            'plan_name', 'start_date', 'end_date', 'status',
            'auto_renew', 'created_at'
        )


class SubscriptionActivateSerializer(serializers.Serializer):
    plan_id = serializers.IntegerField()
    payment_reference = serializers.CharField(required=False, allow_blank=True)
    auto_renew = serializers.BooleanField(default=True)


class SubscriptionRenewSerializer(serializers.Serializer):
    payment_reference = serializers.CharField(required=False, allow_blank=True)
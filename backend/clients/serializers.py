from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """
    Base serializer for client profile.
    """
    user_detail = UserSerializer(source='user', read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Client
        fields = (
            'id',
            'user',
            'user_detail',
            'email',
            'full_name',
            'company_name',
            'preferred_location',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class ClientListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing clients.
    """
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Client
        fields = (
            'id',
            'email',
            'full_name',
            'company_name',
            'preferred_location',
            'created_at',
        )

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class ClientDetailSerializer(ClientSerializer):
    """
    Detailed serializer (same as base).
    """
    pass
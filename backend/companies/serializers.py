from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    owner_detail = UserSerializer(source='owner', read_only=True)
    members_count = serializers.IntegerField(source='members_count', read_only=True)
    is_owner = serializers.SerializerMethodField()
    can_manage = serializers.SerializerMethodField()
    can_invite = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'owner',
            'owner_detail',
            'name',
            'slug',
            'registration_number',
            'description',
            'logo',
            'email',
            'phone',
            'website',
            'address',
            'is_active',
            'is_verified',
            'members_count',
            'is_owner',
            'can_manage',
            'can_invite',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('slug', 'created_at', 'updated_at', 'members_count')

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.owner == request.user
        return False

    def get_can_manage(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_manage(request.user)
        return False

    def get_can_invite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_invite(request.user)
        return False


class CompanyListSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    members_count = serializers.IntegerField(source='members_count', read_only=True)

    class Meta:
        model = Company
        fields = (
            'id',
            'name',
            'slug',
            'logo',
            'owner_email',
            'members_count',
            'is_active',
            'is_verified',
            'created_at',
        )


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'name',
            'registration_number',
            'description',
            'logo',
            'email',
            'phone',
            'website',
            'address',
        )


class CompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'name',
            'registration_number',
            'description',
            'logo',
            'email',
            'phone',
            'website',
            'address',
            'is_active',
            'is_verified',
        )
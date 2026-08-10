from rest_framework import serializers
from .models import Organization, OrganizationMember, OrganizationInvite
from accounts.serializers import UserListSerializer


class OrganizationListSerializer(serializers.ModelSerializer):
    """Minimal fields for list views."""
    member_count = serializers.IntegerField(source='members.count', read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id", "name", "email", "phone",
            "is_active", "member_count", "created_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Full detail view."""
    class Meta:
        model = Organization
        fields = [
            "id", "name", "email", "phone", "address",
            "website", "tax_id", "is_active",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrganizationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "name", "email", "phone", "address",
            "website", "tax_id", "is_active"
        ]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_details = UserListSerializer(source='user', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = OrganizationMember
        fields = [
            "id", "user", "user_email", "user_details",
            "role", "is_active", "joined_at"
        ]
        read_only_fields = ["id", "joined_at", "user_details", "user_email"]


class OrganizationMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMember
        fields = ["user", "role", "is_active"]


class OrganizationInviteSerializer(serializers.ModelSerializer):
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = OrganizationInvite
        fields = [
            "id", "organization", "organization_name",
            "email", "role", "status", "token",
            "invited_by", "invited_by_email",
            "expires_at", "is_expired",
            "accepted_at", "created_at"
        ]
        read_only_fields = [
            "id", "token", "status", "accepted_at",
            "created_at", "is_expired"
        ]


class OrganizationInviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInvite
        fields = ["email", "role"]
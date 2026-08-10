from rest_framework import serializers
from .models import VerificationDocumentType, VerificationRequest
from accounts.serializers import UserSerializer


class VerificationDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDocumentType
        fields = (
            'id', 'name', 'code', 'description', 'is_active',
            'required_for_artisan', 'required_for_client', 'required_for_company'
        )


class VerificationRequestSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    reviewed_by_detail = UserSerializer(source='reviewed_by', read_only=True)
    document_type_detail = VerificationDocumentTypeSerializer(source='document_type', read_only=True)

    class Meta:
        model = VerificationRequest
        fields = (
            'id', 'user', 'user_detail', 'reviewed_by', 'reviewed_by_detail',
            'document_type', 'document_type_detail', 'document', 'document_back',
            'document_number', 'status', 'notes', 'rejection_reason', 'admin_notes',
            'approved_at', 'rejected_at', 'reviewed_at', 'expires_at',
            'ip_address', 'user_agent', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'user', 'status', 'approved_at', 'rejected_at', 'reviewed_at',
            'ip_address', 'user_agent', 'created_at', 'updated_at'
        )


class VerificationRequestListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)

    class Meta:
        model = VerificationRequest
        fields = (
            'id', 'user_email', 'document_type_name', 'status',
            'created_at', 'expires_at'
        )


class VerificationRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationRequest
        fields = ('document_type', 'document', 'document_back', 'document_number', 'notes')


class VerificationRequestActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=['approve', 'reject', 'start_review', 'cancel', 'expire']
    )
    reason = serializers.CharField(required=False, allow_blank=True)
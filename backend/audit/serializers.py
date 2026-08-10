from rest_framework import serializers
from .models import AuditLog
from .choices import AuditAction, AuditSeverity, HttpMethod


class AuditLogListSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "action",
            "severity",
            "module",
            "object_repr",
            "success",
            "response_status",
            "duration_ms",
            "ip_address",
            "path",
            "method",
            "created_at",
        ]
        read_only_fields = "__all__"


class AuditLogDetailSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()
    content_type_name = serializers.CharField(source="content_type.model", read_only=True)

    class Meta:
        model = AuditLog
        fields = "__all__"
        read_only_fields = "__all__"

    def get_user_detail(self, obj):
        from accounts.serializers import UserSerializer
        if obj.user:
            return UserSerializer(obj.user).data
        return None
"""
Client-safe Incident serializers.
"""
from rest_framework import serializers

from .models import Incident


class IncidentClientListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    status_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Incident
        fields = [
            "id", "incident_number", "title", "description",
            "status", "status_id", "priority",
            "created_at", "target_resolution",
        ]
        read_only_fields = fields

    def get_status(self, obj):
        return obj.status.name if obj.status else "NEW"


class IncidentClientDetailSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    status_id = serializers.UUIDField(read_only=True)
    assigned_artisan_name = serializers.SerializerMethodField()
    assigned_artisan_id = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = [
            "id", "incident_number", "title", "description",
            "status", "status_id", "priority", "address",
            "target_resolution", "created_at", "updated_at",
            "assigned_artisan_name", "assigned_artisan_id",
        ]
        read_only_fields = fields

    def get_status(self, obj):
        return obj.status.name if obj.status else "NEW"

    def get_assigned_artisan_name(self, obj):
        u = obj.assigned_to
        if not u:
            return None
        return (
            getattr(u, "get_full_name", lambda: None)()
            or getattr(u, "email", None)
        )

    def get_assigned_artisan_id(self, obj):
        return str(obj.assigned_to_id) if obj.assigned_to_id else None


class IncidentClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [
            "title", "description",
            "category", "subcategory",
            "priority", "address",
        ]

    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Title is required.")
        return value
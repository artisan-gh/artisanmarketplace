from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Customer


class CustomerListSerializer(serializers.ModelSerializer):
    """Minimal fields for list views."""
    class Meta:
        model = Customer
        fields = [
            "id", "name", "phone", "email",
            "address", "organization", "created_at", "is_deleted"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomerDetailSerializer(serializers.ModelSerializer):
    """Full detail view."""
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
        default=None
    )

    class Meta:
        model = Customer
        fields = [
            "id", "name", "phone", "email", "address",
            "gps_lat", "gps_lng", "organization", "organization_name",
            "notes", "tags",
            "created_at", "updated_at", "created_by", "updated_by",
            "is_deleted", "deleted_at"
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "created_by", "updated_by", "is_deleted", "deleted_at"
        ]


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    """For creation and updates – requires phone uniqueness."""
    phone = serializers.CharField(
        max_length=20,
        validators=[UniqueValidator(queryset=Customer.objects.all())]
    )

    class Meta:
        model = Customer
        fields = [
            "name", "phone", "email", "address",
            "gps_lat", "gps_lng", "organization",
            "notes", "tags"
        ]

    def validate_phone(self, value):
        # Ensure phone is unique (excluding soft-deleted)
        if Customer.objects.filter(phone=value, is_deleted=False).exists():
            raise serializers.ValidationError("A customer with this phone already exists.")
        return value

    def create(self, validated_data):
        # Set created_by from context
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Set updated_by
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["updated_by"] = request.user
        return super().update(instance, validated_data)
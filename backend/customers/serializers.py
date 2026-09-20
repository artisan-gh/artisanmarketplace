
from rest_framework import serializers
from .models import Customer


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "phone", "email", "address",
                  "organization", "created_at", "is_deleted"]
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomerDetailSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True, default=None)
    has_account = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ["id", "name", "phone", "email", "address",
                  "gps_lat", "gps_lng", "organization", "organization_name",
                  "notes", "tags", "user", "has_account",
                  "created_at", "updated_at", "created_by", "updated_by",
                  "is_deleted", "deleted_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at",
                            "created_by", "updated_by", "is_deleted", "deleted_at"]

    def get_has_account(self, obj):
        return obj.user_id is not None


class CustomerCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address",
                  "gps_lat", "gps_lng", "organization", "notes", "tags"]

    def validate_phone(self, value):
        value = (value or "").strip()
        qs = Customer.objects.filter(phone=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A customer with this phone already exists.")
        return value

    def create(self, validated_data):
        req = self.context.get("request")
        if req and getattr(req.user, "is_authenticated", False):
            validated_data["created_by"] = req.user
            validated_data["updated_by"] = req.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        req = self.context.get("request")
        if req and getattr(req.user, "is_authenticated", False):
            validated_data["updated_by"] = req.user
        return super().update(instance, validated_data)

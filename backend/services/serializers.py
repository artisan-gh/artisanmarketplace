from rest_framework import serializers

from categories.models import Category, SubCategory
from categories.serializers import (
    CategorySerializer,
    SubCategorySerializer,
)

from .models import Service


# =============================================================================
# SERVICE LIST SERIALIZER
# =============================================================================

class ServiceListSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField()
    subcategory = serializers.StringRelatedField()

    class Meta:
        model = Service

        fields = (
            "id",
            "name",
            "slug",
            "category",
            "subcategory",
            "image",
            "minimum_price",
            "maximum_price",
            "estimated_duration",
            "is_featured",
            "is_active",
        )


# =============================================================================
# SERVICE DETAIL SERIALIZER
# =============================================================================

class ServiceDetailSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)

    class Meta:
        model = Service

        fields = (
            "id",
            "category",
            "subcategory",
            "name",
            "slug",
            "description",
            "image",
            "minimum_price",
            "maximum_price",
            "estimated_duration",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        )


# =============================================================================
# CREATE / UPDATE SERIALIZER
# =============================================================================

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service

        fields = (
            "id",
            "category",
            "subcategory",
            "name",
            "slug",
            "description",
            "image",
            "minimum_price",
            "maximum_price",
            "estimated_duration",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):

        return value.strip().title()

    def validate(self, attrs):

        minimum = attrs.get(
            "minimum_price",
            getattr(self.instance, "minimum_price", 0),
        )

        maximum = attrs.get(
            "maximum_price",
            getattr(self.instance, "maximum_price", 0),
        )

        if maximum < minimum:
            raise serializers.ValidationError(
                {
                    "maximum_price":
                    "Maximum price cannot be less than minimum price."
                }
            )

        return attrs


# =============================================================================
# SIMPLE SERIALIZER
# =============================================================================

class ServiceSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service

        fields = (
            "id",
            "name",
            "slug",
        )


# =============================================================================
# STATISTICS SERIALIZER
# =============================================================================

class ServiceStatisticsSerializer(serializers.Serializer):

    total_services = serializers.IntegerField()

    active_services = serializers.IntegerField()

    featured_services = serializers.IntegerField()

    inactive_services = serializers.IntegerField()
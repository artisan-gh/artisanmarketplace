from rest_framework import serializers

from .models import Category, SubCategory


# =============================================================================
# SUBCATEGORY SERIALIZERS
# =============================================================================

class SubCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for SubCategory.
    """

    category_name = serializers.ReadOnlyField(
        source="category.name"
    )

    category_slug = serializers.ReadOnlyField(
        source="category.slug"
    )

    class Meta:
        model = SubCategory

        fields = (
            "id",
            "category",
            "category_name",
            "category_slug",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):

        category = attrs.get(
            "category",
            getattr(self.instance, "category", None)
        )

        name = attrs.get(
            "name",
            getattr(self.instance, "name", "")
        )

        queryset = SubCategory.objects.filter(
            category=category,
            name__iexact=name.strip()
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():

            raise serializers.ValidationError(
                {
                    "name":
                    "This subcategory already exists."
                }
            )

        return attrs


# =============================================================================
# CATEGORY SERIALIZER
# =============================================================================

class CategorySerializer(serializers.ModelSerializer):
    """
    Full Category Serializer.
    """

    subcategories = SubCategorySerializer(
        many=True,
        read_only=True
    )

    total_subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category

        fields = (
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "image",
            "is_active",
            "total_subcategories",
            "subcategories",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "slug",
            "total_subcategories",
            "created_at",
            "updated_at",
        )

    def get_total_subcategories(self, obj):

        return obj.subcategories.count()

    def validate_name(self, value):

        value = value.strip()

        queryset = Category.objects.filter(
            name__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():

            raise serializers.ValidationError(
                "Category already exists."
            )

        return value


# =============================================================================
# CATEGORY LIST SERIALIZER
# =============================================================================

class CategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing categories.
    """

    total_subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category

        fields = (
            "id",
            "name",
            "slug",
            "icon",
            "image",
            "is_active",
            "total_subcategories",
        )

    def get_total_subcategories(self, obj):

        return obj.subcategories.count()


# =============================================================================
# CATEGORY CREATE / UPDATE
# =============================================================================

class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Used for creating and updating categories.
    """

    class Meta:
        model = Category

        fields = (
            "name",
            "description",
            "icon",
            "image",
            "is_active",
        )

    def validate_name(self, value):

        value = value.strip()

        queryset = Category.objects.filter(
            name__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():

            raise serializers.ValidationError(
                "Category already exists."
            )

        return value


# =============================================================================
# SUBCATEGORY CREATE / UPDATE
# =============================================================================

class SubCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Used for creating and updating subcategories.
    """

    class Meta:
        model = SubCategory

        fields = (
            "category",
            "name",
            "description",
            "is_active",
        )

    def validate(self, attrs):

        category = attrs.get(
            "category",
            getattr(self.instance, "category", None)
        )

        name = attrs.get(
            "name",
            getattr(self.instance, "name", "")
        )

        queryset = SubCategory.objects.filter(
            category=category,
            name__iexact=name.strip()
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():

            raise serializers.ValidationError(
                {
                    "name":
                    "This subcategory already exists."
                }
            )

        return attrs
from rest_framework import serializers
from .models import IncidentCategory, SubCategory


class IncidentCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentCategory
        fields = ['id', 'code', 'name', 'description', 'is_active', 'ordering']
        read_only_fields = ['id', 'code']


class IncidentCategoryDetailSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = IncidentCategory
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

    def get_subcategories(self, obj):
        # Optional: include subcategories in the detail view
        return SubCategorySerializer(obj.subcategories.filter(is_active=True), many=True).data


class IncidentCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentCategory
        fields = ['name', 'description', 'is_active', 'ordering']


class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_code = serializers.CharField(source='category.code', read_only=True)

    class Meta:
        model = SubCategory
        fields = [
            'id', 'code', 'name', 'category', 'category_name', 'category_code',
            'description', 'is_active', 'ordering', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class SubCategoryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description', 'is_active', 'ordering']
 
class IncidentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentCategory
        fields = ['id', 'name', 'description', 'is_active', 'ordering', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'name', 'description', 'is_active', 'ordering', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']        
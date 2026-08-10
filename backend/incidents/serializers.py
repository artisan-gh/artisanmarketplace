from rest_framework import serializers
from .models import Incident
from customers.serializers import CustomerListSerializer
from accounts.serializers import UserListSerializer
from incident_category.serializers import (
    IncidentCategoryListSerializer,
    SubCategorySerializer,  # ✅ Import the subcategory serializer
)
from incident_statuses.serializers import IncidentStatusListSerializer


class IncidentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)  # ✅ Added
    status_name = serializers.CharField(source='status.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = Incident
        fields = [
            'id', 'incident_number', 'title', 'priority', 'customer_name',
            'category_name', 'subcategory_name', 'status_name', 'assigned_to_name',
            'created_at', 'target_resolution', 'resolved_at'
        ]
        read_only_fields = ['id', 'incident_number', 'created_at']


class IncidentDetailSerializer(serializers.ModelSerializer):
    customer_detail = CustomerListSerializer(source='customer', read_only=True)
    category_detail = IncidentCategoryListSerializer(source='category', read_only=True)
    subcategory_detail = SubCategorySerializer(source='subcategory', read_only=True)  # ✅ Added
    status_detail = IncidentStatusListSerializer(source='status', read_only=True)
    created_by_detail = UserListSerializer(source='created_by', read_only=True)
    assigned_to_detail = UserListSerializer(source='assigned_to', read_only=True)
    supervisor_detail = UserListSerializer(source='supervisor', read_only=True)

    class Meta:
        model = Incident
        fields = '__all__'
        read_only_fields = ['id', 'incident_number', 'created_at', 'updated_at']


class IncidentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [
            'customer', 'category', 'subcategory', 'priority', 'status', 'title',  # ✅ Added 'subcategory'
            'description', 'assigned_to', 'supervisor',
            'target_resolution', 'location_lat', 'location_lng', 'address'
        ]

    def validate(self, data):
        if not data.get('target_resolution'):
            raise serializers.ValidationError("Target resolution is required.")
        return data
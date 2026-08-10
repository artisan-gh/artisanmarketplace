from rest_framework import serializers
from .models import IncidentPriority

class IncidentPriorityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentPriority
        fields = ['id', 'code', 'name', 'description', 'is_active', 'ordering', 'color_code']
        read_only_fields = ['id', 'code']

class IncidentPriorityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentPriority
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

class IncidentPriorityCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentPriority
        fields = ['name', 'description', 'is_active', 'ordering', 'resolution_hours', 'escalation_hours', 'color_code']
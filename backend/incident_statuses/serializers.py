from rest_framework import serializers
from .models import IncidentStatus

class IncidentStatusListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentStatus
        fields = ['id', 'code', 'name', 'is_active', 'ordering', 'color_code', 'is_terminal']
        read_only_fields = ['id', 'code']

class IncidentStatusDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentStatus
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']

class IncidentStatusCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentStatus
        fields = ['name', 'description', 'is_active', 'ordering', 'color_code', 'is_terminal']
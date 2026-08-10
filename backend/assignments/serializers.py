from rest_framework import serializers
from .models import Assignment
from incidents.serializers import IncidentListSerializer
from accounts.serializers import UserListSerializer

class AssignmentListSerializer(serializers.ModelSerializer):
    incident_number = serializers.CharField(source='incident.incident_number', read_only=True)
    artisan_name = serializers.CharField(source='artisan.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'incident', 'incident_number', 'artisan', 'artisan_name',
            'assigned_by', 'assigned_by_name', 'status', 'assigned_at',
            'accepted_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'accepted_at', 'started_at', 'completed_at']


class AssignmentDetailSerializer(serializers.ModelSerializer):
    incident_detail = IncidentListSerializer(source='incident', read_only=True)
    artisan_detail = UserListSerializer(source='artisan', read_only=True)
    assigned_by_detail = UserListSerializer(source='assigned_by', read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['id', 'assigned_at', 'accepted_at', 'started_at', 'completed_at']


class AssignmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['incident', 'artisan', 'notes']
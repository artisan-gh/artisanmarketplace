from rest_framework import serializers
from django.utils import timezone
from .models import SLAPolicy, SLATracker
from incidents.serializers import IncidentListSerializer


class SLAPolicyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SLAPolicy
        fields = ['id', 'name', 'priority', 'resolution_hours', 'is_active']
        read_only_fields = ['id']


class SLAPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SLAPolicy
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SLATrackerListSerializer(serializers.ModelSerializer):
    incident_number = serializers.CharField(source='incident.incident_number', read_only=True)
    sla_status = serializers.CharField(source='status', read_only=True)
    remaining_time = serializers.SerializerMethodField()
    target_resolution = serializers.DateTimeField(source='incident.target_resolution', read_only=True)
    customer_name = serializers.CharField(source='incident.customer.name', read_only=True)
    priority = serializers.CharField(source='incident.priority', read_only=True)

    class Meta:
        model = SLATracker
        fields = [
            'id',
            'incident',
            'incident_number',
            'customer_name',
            'priority',
            'sla_status',
            'target_resolution',
            'remaining_time',
            'target_escalation',
            'resolved_at',
            'escalated_at',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_remaining_time(self, obj):
        """
        Compute remaining time until breach.
        Returns a human-readable string like "2h 15m" or "Breached" if overdue.
        """
        now = timezone.now()
        target = obj.incident.target_resolution
        if not target:
            return None
        if now > target:
            return 'Breached'
        delta = target - now
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        return f"{int(minutes)}m"


class SLATrackerSerializer(serializers.ModelSerializer):
    incident_detail = IncidentListSerializer(source='incident', read_only=True)
    sla_status = serializers.CharField(source='status', read_only=True)
    remaining_time = serializers.SerializerMethodField()
    target_resolution = serializers.DateTimeField(source='incident.target_resolution', read_only=True)
    customer_name = serializers.CharField(source='incident.customer.name', read_only=True)
    priority = serializers.CharField(source='incident.priority', read_only=True)

    class Meta:
        model = SLATracker
        fields = [
            'id',
            'incident',
            'incident_detail',
            'customer_name',
            'priority',
            'policy',
            'sla_status',
            'target_resolution',
            'remaining_time',
            'target_escalation',
            'resolved_at',
            'escalated_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_remaining_time(self, obj):
        now = timezone.now()
        target = obj.incident.target_resolution
        if not target:
            return None
        if now > target:
            return 'Breached'
        delta = target - now
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        return f"{int(minutes)}m"
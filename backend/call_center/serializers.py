from rest_framework import serializers
from .models import CallLog
from customers.serializers import CustomerListSerializer
from incidents.serializers import IncidentListSerializer
from accounts.serializers import UserListSerializer


class CallLogListSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    incident_number = serializers.CharField(source='incident.incident_number', read_only=True)

    class Meta:
        model = CallLog
        fields = [
            'id', 'reference', 'agent', 'agent_name',
            'customer', 'customer_name', 'incident', 'incident_number',
            'direction', 'channel', 'caller_number',
            'started_at', 'ended_at', 'duration_seconds',
            'status', 'disposition', 'notes',
            'follow_up_required', 'follow_up_date', 'rating',
            'created_at'
        ]
        read_only_fields = ['id', 'reference', 'duration_seconds', 'created_at']


class CallLogDetailSerializer(serializers.ModelSerializer):
    agent_detail = UserListSerializer(source='agent', read_only=True)
    customer_detail = CustomerListSerializer(source='customer', read_only=True)
    incident_detail = IncidentListSerializer(source='incident', read_only=True)

    class Meta:
        model = CallLog
        fields = '__all__'
        read_only_fields = ['id', 'reference', 'duration_seconds', 'created_at', 'updated_at']


class CallLogCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallLog
        fields = [
            'customer', 'incident', 'direction', 'channel',
            'caller_number', 'started_at', 'ended_at', 'notes',
            'status', 'disposition', 'follow_up_required',
            'follow_up_date', 'rating'
        ]
        read_only_fields = ['reference']
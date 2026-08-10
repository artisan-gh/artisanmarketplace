# notifications/serializers.py
from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserListSerializer


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for notification lists.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    incident_number = serializers.CharField(source='incident.incident_number', read_only=True, default=None)
    assignment_id = serializers.CharField(source='assignment.id', read_only=True, default=None)

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'notification_type',
            'channel',
            'subject',
            'message',
            'incident',
            'incident_number',
            'assignment',
            'assignment_id',
            'is_read',
            'sent_at',
        ]
        read_only_fields = ['id', 'sent_at']

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email


class NotificationDetailSerializer(serializers.ModelSerializer):
    """
    Full detail serializer including the data JSON field.
    """
    user_detail = UserListSerializer(source='user', read_only=True)
    incident_number = serializers.CharField(source='incident.incident_number', read_only=True, default=None)
    assignment_id = serializers.CharField(source='assignment.id', read_only=True, default=None)

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'user_detail',
            'notification_type',
            'channel',
            'subject',
            'message',
            'incident',
            'incident_number',
            'assignment',
            'assignment_id',
            'data',
            'is_read',
            'read_at',
            'sent_at',
        ]
        read_only_fields = ['id', 'sent_at', 'read_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new notification.
    The `user` field is automatically set from the request context.
    """
    class Meta:
        model = Notification
        fields = [
            'user',
            'incident',
            'assignment',
            'notification_type',
            'channel',
            'subject',
            'message',
            'data',
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        # Ensure the user is set from the request context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class NotificationMarkReadSerializer(serializers.Serializer):
    """
    Serializer for marking a single notification as read.
    """
    notification_id = serializers.UUIDField(required=True)


class NotificationMarkAllReadSerializer(serializers.Serializer):
    """
    Serializer for marking all notifications as read.
    """
    pass  # No fields needed – just a POST action


class NotificationUnreadCountSerializer(serializers.Serializer):
    """
    Serializer for the unread count response.
    """
    count = serializers.IntegerField()
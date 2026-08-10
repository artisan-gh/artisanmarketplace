from rest_framework import serializers
from .models import SupportTicket, SupportReply
from accounts.serializers import UserSerializer


class SupportReplySerializer(serializers.ModelSerializer):
    responder_name = serializers.CharField(source='responder.get_full_name', read_only=True)

    class Meta:
        model = SupportReply
        fields = (
            'id', 'ticket', 'responder', 'responder_name',
            'message', 'is_internal', 'attachment', 'created_at'
        )
        read_only_fields = ('created_at',)


class SupportTicketSerializer(serializers.ModelSerializer):
    replies = SupportReplySerializer(many=True, read_only=True)
    user_detail = UserSerializer(source='user', read_only=True)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    reply_count = serializers.IntegerField(source='replies.count', read_only=True)

    class Meta:
        model = SupportTicket
        fields = (
            'id', 'user', 'user_detail', 'assigned_to', 'assigned_to_detail',
            'subject', 'message', 'category', 'priority', 'status',
            'resolved_at', 'closed_at', 'is_public', 'attachment',
            'replies', 'reply_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'status', 'resolved_at', 'closed_at', 'created_at', 'updated_at')


class SupportTicketListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    reply_count = serializers.IntegerField(source='replies.count', read_only=True)

    class Meta:
        model = SupportTicket
        fields = (
            'id', 'subject', 'user_email', 'assigned_to_name',
            'category', 'priority', 'status', 'reply_count', 'created_at'
        )


class SupportReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportReply
        fields = ('ticket', 'message', 'is_internal', 'attachment')


class SupportTicketStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=SupportTicket.Status.choices)
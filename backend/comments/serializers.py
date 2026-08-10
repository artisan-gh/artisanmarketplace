from rest_framework import serializers
from .models import Comment
from accounts.serializers import UserListSerializer

class CommentSerializer(serializers.ModelSerializer):
    user_detail = UserListSerializer(source='user', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'incident', 'user', 'user_name', 'user_detail', 'text', 'is_internal', 'created_at']
        read_only_fields = ['id', 'created_at', 'user_name', 'user_detail']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['incident', 'text', 'is_internal']
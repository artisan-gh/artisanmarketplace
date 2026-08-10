from rest_framework import serializers
from .models import Attachment

class AttachmentListSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model = Attachment
        fields = ['id', 'filename', 'file_type', 'file', 'uploaded_by_name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

class AttachmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['incident', 'file', 'filename', 'file_type', 'description']
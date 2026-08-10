from rest_framework import serializers
from .models import MediaFile
from accounts.serializers import UserSerializer


class MediaFileSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = MediaFile
        fields = (
            'id', 'user', 'user_detail', 'file', 'url', 'thumbnail', 'thumbnail_url',
            'file_name', 'file_size', 'mime_type', 'file_type', 'category', 'category_display',
            'width', 'height', 'content_type', 'object_id', 'is_public', 'expires_at',
            'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('user', 'file_size', 'mime_type', 'file_type', 'width', 'height',
                            'created_at', 'updated_at', 'url', 'thumbnail_url')

    def get_url(self, obj):
        return obj.url

    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url


class MediaFileListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = ('id', 'file_name', 'url', 'thumbnail_url', 'file_type', 'category', 'file_size', 'created_at')

    def get_url(self, obj):
        return obj.url

    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url


class MediaFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = ('file', 'category', 'content_type', 'object_id', 'is_public', 'expires_at')


class MediaFileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = ('category', 'is_public', 'is_active', 'expires_at')
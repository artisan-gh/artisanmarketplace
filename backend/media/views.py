from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import models  # <-- added this import
from .models import MediaFile
from .serializers import (
    MediaFileSerializer,
    MediaFileListSerializer,
    MediaFileUploadSerializer,
    MediaFileUpdateSerializer,
)


class MediaFileViewSet(viewsets.ModelViewSet):
    queryset = MediaFile.objects.filter(is_active=True).select_related('user').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'file_type', 'content_type', 'object_id', 'is_public']
    search_fields = ['file_name']
    ordering_fields = ['created_at', 'file_size']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        # Users see their own files and public files
        return self.queryset.filter(models.Q(user=user) | models.Q(is_public=True))

    def get_serializer_class(self):
        if self.action == 'list':
            return MediaFileListSerializer
        if self.action == 'create':
            return MediaFileUploadSerializer
        if self.action in ['update', 'partial_update']:
            return MediaFileUpdateSerializer
        return MediaFileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Dedicated upload endpoint for multipart/form-data.
        """
        serializer = MediaFileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        media = MediaFile(
            user=request.user,
            file=file_obj,
            category=serializer.validated_data.get('category', MediaFile.FileCategory.OTHER),
            content_type=serializer.validated_data.get('content_type'),
            object_id=serializer.validated_data.get('object_id'),
            is_public=serializer.validated_data.get('is_public', False),
            expires_at=serializer.validated_data.get('expires_at')
        )
        media.save()
        return Response(MediaFileSerializer(media).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        media = self.get_object()
        if not media.is_active:
            return Response({'error': 'File not available.'}, status=status.HTTP_404_NOT_FOUND)
        if media.is_expired:
            return Response({'error': 'File has expired.'}, status=status.HTTP_410_GONE)
        response = HttpResponse(media.file.open('rb'), content_type=media.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{media.file_name}"'
        return response

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        media = self.get_object()
        media.soft_delete()
        return Response({'status': 'deleted'})

    @action(detail=False, methods=['get'])
    def my_files(self, request):
        qs = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        qs = self.get_queryset().filter(user=request.user).order_by('-created_at')[:20]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

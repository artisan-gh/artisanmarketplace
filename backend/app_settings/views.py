from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from .models import AppSetting
from .serializers import (
    AppSettingSerializer,
    AppSettingPublicSerializer,
    AppSettingUpdateSerializer,
)


class AppSettingViewSet(viewsets.ModelViewSet):
    queryset = AppSetting.objects.all()
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['group', 'is_public', 'is_editable']
    search_fields = ['key', 'description']
    ordering_fields = ['key', 'group']
    ordering = ['group', 'key']

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return AppSettingUpdateSerializer
        return AppSettingSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public(self, request):
        """Get all public settings (no auth required)."""
        settings = AppSetting.objects.filter(is_public=True)
        serializer = AppSettingPublicSerializer(settings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def refresh_cache(self, request):
        """Refresh the settings cache."""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        # Clear all setting caches
        keys = AppSetting.objects.values_list('key', flat=True)
        for key in keys:
            cache.delete(f'setting_{key}')
        return Response({'status': 'cache_refreshed', 'keys_cleared': len(keys)})

    @action(detail=False, methods=['get'])
    def by_group(self, request):
        """Get settings grouped by group."""
        group = request.query_params.get('group')
        if not group:
            return Response({'error': 'group parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        settings = self.get_queryset().filter(group=group)
        serializer = self.get_serializer(settings, many=True)
        return Response(serializer.data)

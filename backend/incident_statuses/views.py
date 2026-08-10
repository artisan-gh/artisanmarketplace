from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import IncidentStatus
from .serializers import (
    IncidentStatusListSerializer,
    IncidentStatusDetailSerializer,
    IncidentStatusCreateUpdateSerializer,
)
from accounts.permissions import IsAdminOrStaff

class IncidentStatusViewSet(viewsets.ModelViewSet):
    queryset = IncidentStatus.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'ordering', 'created_at']
    ordering = ['ordering', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return IncidentStatusListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return IncidentStatusCreateUpdateSerializer
        return IncidentStatusDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrStaff]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

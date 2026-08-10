# incident_category/views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import IncidentCategory, SubCategory
from .serializers import (
    IncidentCategoryListSerializer,
    IncidentCategoryDetailSerializer,
    IncidentCategoryCreateUpdateSerializer,
    SubCategorySerializer,
)
from accounts.permissions import IsAdminOrStaff


# ─── Public endpoints (no authentication) ──────────────────

class PublicIncidentCategoryListView(ListAPIView):
    """Public endpoint for categories – used by registration."""
    queryset = IncidentCategory.objects.filter(is_active=True)
    serializer_class = IncidentCategoryListSerializer  # uses list serializer
    permission_classes = [AllowAny]


class PublicSubCategoryListView(ListAPIView):
    """Public endpoint for subcategories by category – used by registration."""
    serializer_class = SubCategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.request.query_params.get('category')
        if category_id:
            return SubCategory.objects.filter(category_id=category_id, is_active=True)
        return SubCategory.objects.none()


# ─── Existing viewsets ──────────────────────────────────────

class IncidentCategoryViewSet(viewsets.ModelViewSet):
    queryset = IncidentCategory.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'ordering', 'created_at']
    ordering = ['ordering', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return IncidentCategoryListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return IncidentCategoryCreateUpdateSerializer
        return IncidentCategoryDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrStaff]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read‑only viewset for subcategories.
    Supports filtering by category using ?category=<uuid>.
    """
    queryset = SubCategory.objects.filter(is_active=True)
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category']
    ordering_fields = ['ordering', 'name']
    ordering = ['ordering', 'name']

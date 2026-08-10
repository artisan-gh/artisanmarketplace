from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Service
from .serializers import (
    ServiceSerializer,
    ServiceListSerializer,
    ServiceDetailSerializer,
    ServiceStatisticsSerializer,
)


# =============================================================================
# SERVICE VIEWSET
# =============================================================================

class ServiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing services.
    """

    queryset = (
        Service.objects
        .select_related(
            "category",
            "subcategory",
        )
        .all()
    )

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "category",
        "subcategory",
        "is_active",
        "is_featured",
    ]

    search_fields = [
        "name",
        "description",
        "category__name",
        "subcategory__name",
    ]

    ordering_fields = [
        "name",
        "minimum_price",
        "maximum_price",
        "estimated_duration",
        "created_at",
    ]

    ordering = [
        "name",
    ]

    # -------------------------------------------------------------------------
    # Serializer Selection
    # -------------------------------------------------------------------------

    def get_serializer_class(self):

        if self.action == "list":
            return ServiceListSerializer

        if self.action == "retrieve":
            return ServiceDetailSerializer

        return ServiceSerializer

    # -------------------------------------------------------------------------
    # Active Services
    # -------------------------------------------------------------------------

    @action(
        detail=False,
        methods=["get"],
    )
    def active(self, request):

        queryset = self.filter_queryset(
            self.get_queryset().filter(
                is_active=True
            )
        )

        serializer = ServiceListSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    # -------------------------------------------------------------------------
    # Featured Services
    # -------------------------------------------------------------------------

    @action(
        detail=False,
        methods=["get"],
    )
    def featured(self, request):

        queryset = self.filter_queryset(
            self.get_queryset().filter(
                is_featured=True,
                is_active=True,
            )
        )

        serializer = ServiceListSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAdminUser],
    )
    def statistics(self, request):

        data = {
            "total_services": Service.objects.count(),
            "active_services": Service.objects.filter(
                is_active=True
            ).count(),
            "featured_services": Service.objects.filter(
                is_featured=True
            ).count(),
            "inactive_services": Service.objects.filter(
                is_active=False
            ).count(),
        }

        serializer = ServiceStatisticsSerializer(data)

        return Response(serializer.data)

    # -------------------------------------------------------------------------
    # Services by Category
    # -------------------------------------------------------------------------

    @action(
        detail=False,
        methods=["get"],
        url_path=r"category/(?P<category_id>\d+)",
    )
    def by_category(self, request, category_id=None):

        queryset = self.filter_queryset(
            self.get_queryset().filter(
                category_id=category_id,
                is_active=True,
            )
        )

        serializer = ServiceListSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)

    # -------------------------------------------------------------------------
    # Services by SubCategory
    # -------------------------------------------------------------------------

    @action(
        detail=False,
        methods=["get"],
        url_path=r"subcategory/(?P<subcategory_id>\d+)",
    )
    def by_subcategory(self, request, subcategory_id=None):

        queryset = self.filter_queryset(
            self.get_queryset().filter(
                subcategory_id=subcategory_id,
                is_active=True,
            )
        )

        serializer = ServiceListSerializer(
            queryset,
            many=True,
        )

        return Response(serializer.data)
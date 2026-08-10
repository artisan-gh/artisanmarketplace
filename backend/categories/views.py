from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from .models import Category, SubCategory
from .serializers import (
    CategorySerializer,
    CategoryListSerializer,
    CategoryCreateUpdateSerializer,
    SubCategorySerializer,
    SubCategoryCreateUpdateSerializer,
)


# =============================================================================
# CATEGORY VIEWSET
# =============================================================================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Categories.
    """

    queryset = Category.objects.all()

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "is_active",
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = [
        "name",
    ]

    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve",
            "active",
        ]:
            permission_classes = [
                permissions.AllowAny
            ]
        else:
            permission_classes = [
                permissions.IsAuthenticated,
                permissions.IsAdminUser,
            ]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):

        if self.action == "list":
            return CategoryListSerializer

        if self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            return CategoryCreateUpdateSerializer

        return CategorySerializer

    @swagger_auto_schema(
        operation_summary="List Active Categories"
    )
    @action(
        detail=False,
        methods=["get"]
    )
    def active(self, request):

        queryset = Category.objects.filter(
            is_active=True
        )

        serializer = CategoryListSerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Category Statistics"
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAdminUser]
    )
    def statistics(self, request):

        return Response({

            "total_categories":
            Category.objects.count(),

            "active_categories":
            Category.objects.filter(
                is_active=True
            ).count(),

            "inactive_categories":
            Category.objects.filter(
                is_active=False
            ).count(),

        })


# =============================================================================
# SUBCATEGORY VIEWSET
# =============================================================================

class SubCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoints for SubCategories.
    """

    queryset = SubCategory.objects.select_related(
        "category"
    )

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "category",
        "is_active",
    ]

    search_fields = [
        "name",
        "description",
        "category__name",
    ]

    ordering_fields = [
        "name",
        "created_at",
    ]

    ordering = [
        "name",
    ]

    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve",
            "active",
        ]:
            permission_classes = [
                permissions.AllowAny
            ]
        else:
            permission_classes = [
                permissions.IsAuthenticated,
                permissions.IsAdminUser,
            ]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):

        if self.action in [
            "create",
            "update",
            "partial_update",
        ]:
            return SubCategoryCreateUpdateSerializer

        return SubCategorySerializer

    @swagger_auto_schema(
        operation_summary="List Active SubCategories"
    )
    @action(
        detail=False,
        methods=["get"]
    )
    def active(self, request):

        queryset = SubCategory.objects.filter(
            is_active=True
        )

        serializer = SubCategorySerializer(
            queryset,
            many=True
        )

        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="SubCategory Statistics"
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAdminUser]
    )
    def statistics(self, request):

        return Response({

            "total_subcategories":
            SubCategory.objects.count(),

            "active_subcategories":
            SubCategory.objects.filter(
                is_active=True
            ).count(),

            "inactive_subcategories":
            SubCategory.objects.filter(
                is_active=False
            ).count(),

        })

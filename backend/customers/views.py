from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Customer
from .serializers import (
    CustomerListSerializer,
    CustomerDetailSerializer,
    CustomerCreateUpdateSerializer
)
from accounts.permissions import IsAdmin, IsAgent, IsArtisan, IsDispatcher, IsSupervisor, IsManager


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Customer CRUD.
    - Agents & Admins: full access (create, update, delete)
    - Artisans, Dispatchers, Supervisors, Managers: read-only
    - All authenticated users can list and retrieve.
    """
    queryset = Customer.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["organization", "is_deleted"]
    search_fields = ["name", "phone", "email", "address"]
    ordering_fields = ["name", "created_at", "phone"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return CustomerListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return CustomerCreateUpdateSerializer
        return CustomerDetailSerializer

    def get_permissions(self):
        # Only agents and admins can create, update, delete
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAgent | IsAdmin]
        elif self.action == "restore":
            self.permission_classes = [IsAdmin]  # only admins can restore
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete (override default hard delete)
        instance.soft_delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted customer (admin only).
        """
        customer = Customer.objects.get(pk=pk, is_deleted=True)
        customer.restore()
        return Response({"status": "restored"})

    @action(detail=False, methods=["get"], url_path="search")
    def search_customers(self, request):
        """
        Quick search by name, phone, or email.
        Used by agents when a call comes in.
        """
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"results": []})

        customers = Customer.objects.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query),
            is_deleted=False
        )[:20]  # limit results

        serializer = CustomerListSerializer(customers, many=True)
        return Response({"results": serializer.data})

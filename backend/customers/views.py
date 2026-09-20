
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAgent, IsDispatcher
from .models import Customer
from .serializers import (
    CustomerCreateUpdateSerializer,
    CustomerDetailSerializer,
    CustomerListSerializer,
)

STAFF_TYPES = {"ADMIN", "AGENT", "DISPATCHER", "SUPERVISOR", "MANAGER"}


class IsStaffOrOwner(permissions.BasePermission):
    message = "You do not have access to this customer."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        u = request.user
        ut = (getattr(u, "user_type", "") or "").upper()
        if ut in STAFF_TYPES: return True
        if ut == "CLIENT": return obj.user_id == u.id
        if ut == "ARTISAN": return request.method in permissions.SAFE_METHODS
        return False


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["organization", "is_deleted"]
    search_fields = ["name", "phone", "email", "address"]
    ordering_fields = ["name", "created_at", "phone"]
    ordering = ["-created_at"]
    lookup_value_regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    def get_queryset(self):
        qs = Customer.objects.filter(is_deleted=False).select_related("user", "organization")
        u = self.request.user
        ut = (getattr(u, "user_type", "") or "").upper()
        if ut in STAFF_TYPES: return qs
        if ut == "CLIENT": return qs.filter(user=u)
        if ut == "ARTISAN":
            return qs.filter(invoices__incident__assignments__artisan=u).distinct()
        return qs.none()

    def get_serializer_class(self):
        if self.action == "list": return CustomerListSerializer
        if self.action in ("create", "update", "partial_update"): return CustomerCreateUpdateSerializer
        return CustomerDetailSerializer

    def get_permissions(self):
        if self.action in ("create", "destroy", "restore"):
            self.permission_classes = [IsAgent | IsAdmin]
        elif self.action in ("update", "partial_update"):
            self.permission_classes = [IsAgent | IsAdmin | IsStaffOrOwner]
        elif self.action == "search_customers":
            self.permission_classes = [IsAgent | IsAdmin | IsDispatcher]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        u = request.user
        ut = (getattr(u, "user_type", "") or "").upper()
        if ut != "CLIENT":
            return Response({"detail": "Only client accounts can use this endpoint."},
                            status=status.HTTP_403_FORBIDDEN)
        customer = Customer.objects.filter(user=u, is_deleted=False).first()
        if not customer:
            return Response({"detail": "No customer profile linked to this account."},
                            status=status.HTTP_404_NOT_FOUND)
        if request.method == "PATCH":
            ALLOWED = {"name", "email", "address", "gps_lat", "gps_lng"}
            data = {k: v for k, v in request.data.items() if k in ALLOWED}
            ser = CustomerCreateUpdateSerializer(customer, data=data, partial=True,
                                                 context={"request": request})
            ser.is_valid(raise_exception=True)
            ser.save(updated_by=u)
            return Response(CustomerDetailSerializer(customer).data)
        return Response(CustomerDetailSerializer(customer).data)

    @action(detail=False, methods=["get"], url_path="search", url_name="search")
    def search_customers(self, request):
        query = (request.query_params.get("q") or "").strip()
        if not query:
            return Response({"results": []})
        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query),
            is_deleted=False,
        )[:20]
        return Response({"results": CustomerListSerializer(customers, many=True).data})

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        customer = Customer.objects.get(pk=pk, is_deleted=True)
        customer.restore()
        return Response({"status": "restored"})

"""Client-facing Incident endpoints."""
from datetime import timedelta

from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Incident
from .serializers_client import (
    IncidentClientCreateSerializer,
    IncidentClientDetailSerializer,
    IncidentClientListSerializer,
)


class IsClient(permissions.BasePermission):
    message = "Only client accounts can use this endpoint."

    def has_permission(self, request, view):
        u = request.user
        return (
            u and u.is_authenticated
            and (getattr(u, "user_type", "") or "").upper() == "CLIENT"
        )


def _default_status_for_incident():
    """
    Find the initial IncidentStatus to assign to a freshly created incident.
    Tries common spellings first, then falls back to the first row.
    """
    try:
        status_model = Incident._meta.get_field("status").related_model
    except Exception:
        return None

    if status_model is None:
        return None

    for candidate in ("NEW", "New", "new", "PENDING", "Pending",
                      "OPEN", "Open", "DRAFT", "Draft"):
        try:
            obj = status_model.objects.filter(name__iexact=candidate).first()
            if obj:
                return obj
        except Exception:
            continue

    try:
        return status_model.objects.first()
    except Exception:
        return None


class IncidentClientViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsClient]

    def get_queryset(self):
        u = self.request.user
        customer = getattr(u, "customer", None)
        if not customer:
            return Incident.objects.none()
        return Incident.objects.filter(customer=customer).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return IncidentClientCreateSerializer
        if self.action == "list":
            return IncidentClientListSerializer
        return IncidentClientDetailSerializer

    def perform_create(self, serializer):
        u = self.request.user
        customer = getattr(u, "customer", None)
        if not customer:
            raise PermissionDenied("No customer profile linked to this account.")

        extra = {"customer": customer, "created_by": u}

        if not serializer.validated_data.get("target_resolution"):
            extra["target_resolution"] = timezone.now() + timedelta(hours=24)

        if not serializer.validated_data.get("status"):
            default_status = _default_status_for_incident()
            if default_status is not None:
                extra["status"] = default_status

        serializer.save(**extra)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        detail = IncidentClientDetailSerializer(
            serializer.instance, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(detail.data)
        return Response(
            detail.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
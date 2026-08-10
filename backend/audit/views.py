from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog
from .serializers import AuditLogListSerializer, AuditLogDetailSerializer
from .filters import AuditLogFilter
from .permissions import CanViewAuditLogs


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs.
    Only accessible by staff or users with explicit permission.
    """
    queryset = AuditLog.objects.select_related("user", "organization")
    permission_classes = [permissions.IsAuthenticated, CanViewAuditLogs]
    serializer_class = AuditLogListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuditLogFilter
    search_fields = ["user__email", "module", "object_repr", "description"]
    ordering_fields = ["created_at", "duration_ms", "response_status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AuditLogDetailSerializer
        return AuditLogListSerializer

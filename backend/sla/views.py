from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from .models import SLAPolicy, SLATracker
from .serializers import (
    SLAPolicySerializer,
    SLAPolicyListSerializer,
    SLATrackerSerializer,
    SLATrackerListSerializer
)
from accounts.permissions import IsAdminOrStaff


class SLAPolicyViewSet(viewsets.ModelViewSet):
    queryset = SLAPolicy.objects.filter(is_active=True)
    permission_classes = [IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'priority']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['priority', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return SLAPolicyListSerializer
        return SLAPolicySerializer


class SLATrackerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SLATracker.objects.select_related('incident', 'policy')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SLATrackerListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'incident']
    search_fields = ['incident__incident_number']
    ordering_fields = ['created_at', 'target_resolution']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SLATrackerSerializer
        return SLATrackerListSerializer

    @action(detail=False, methods=['get'], url_path='breached')
    def breached(self, request):
        trackers = self.get_queryset().filter(status='BREACHED')
        serializer = SLATrackerListSerializer(trackers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='at-risk')
    def at_risk(self, request):
        trackers = self.get_queryset().filter(status='AT_RISK')
        serializer = SLATrackerListSerializer(trackers, many=True)
        return Response(serializer.data)

    # ─── NEW: Get SLA tracker by incident ID ──────────────────
    @action(detail=False, methods=['get'], url_path='incident/(?P<incident_id>[^/.]+)')
    def get_by_incident(self, request, incident_id=None):
        """
        Retrieve the SLA tracker for a specific incident.
        """
        try:
            tracker = SLATracker.objects.select_related('incident', 'policy').get(incident_id=incident_id)
            serializer = self.get_serializer(tracker)
            return Response(serializer.data)
        except SLATracker.DoesNotExist:
            return Response(
                {'error': 'No SLA tracker found for this incident.'},
                status=status.HTTP_404_NOT_FOUND
            )

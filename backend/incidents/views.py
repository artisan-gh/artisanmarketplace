# incidents/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as drf_filters
from django.db.models import Q
from django.utils import timezone

from .models import Incident
from .serializers import (
    IncidentListSerializer,
    IncidentDetailSerializer,
    IncidentCreateUpdateSerializer,
)
from accounts.permissions import IsAdminOrStaff, IsAgent, IsArtisan, IsDispatcher, IsSupervisor

# ─── Import Assignment model ────────────────────────────────
from assignments.models import Assignment


class IncidentFilter(drf_filters.FilterSet):
    """
    Custom filters for Incident.
    - Accepts status name (e.g., 'NEW') instead of ID.
    - Accepts priority name (e.g., 'HIGH').
    """
    status = drf_filters.CharFilter(field_name='status__name', lookup_expr='iexact')
    priority = drf_filters.CharFilter(field_name='priority', lookup_expr='iexact')
    category = drf_filters.UUIDFilter(field_name='category_id')
    subcategory = drf_filters.UUIDFilter(field_name='subcategory_id')
    assigned_to = drf_filters.UUIDFilter(field_name='assigned_to_id')
    customer = drf_filters.UUIDFilter(field_name='customer_id')

    class Meta:
        model = Incident
        fields = ['status', 'priority', 'category', 'subcategory', 'assigned_to', 'customer']


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = IncidentFilter
    search_fields = [
        'incident_number', 'title', 'description',
        'customer__name', 'customer__phone'
    ]
    ordering_fields = ['created_at', 'target_resolution', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return IncidentListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return IncidentCreateUpdateSerializer
        return IncidentDetailSerializer

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAgent | IsAdminOrStaff]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAgent | IsAdminOrStaff | IsSupervisor]
        elif self.action in ['destroy']:
            self.permission_classes = [IsAdminOrStaff]
        elif self.action in ['assign', 'reassign']:
            self.permission_classes = [IsDispatcher | IsAdminOrStaff]
        elif self.action in ['accept', 'start', 'complete']:
            self.permission_classes = [IsArtisan]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign an incident to an artisan.
        Creates an Assignment record and updates the incident's assigned_to field.
        """
        print("🔵 === assign action called ===")
        incident = self.get_object()
        print(f"🔵 Incident: {incident.id} - {incident.incident_number}")

        artisan_id = request.data.get('assigned_to')
        print(f"🔵 artisan_id received: {artisan_id}")

        if not artisan_id:
            return Response({'error': 'assigned_to is required'}, status=status.HTTP_400_BAD_REQUEST)

        # ─── 1. Update incident ──────────────────────────────
        incident.assigned_to_id = artisan_id
        incident.save(update_fields=['assigned_to'])
        print(f"🟢 Incident updated with artisan {artisan_id}")

        # ─── 2. Create or update the Assignment ──────────────
        try:
            # Use update_or_create to handle existing assignments
            assignment, created = Assignment.objects.update_or_create(
                incident=incident,
                defaults={
                    'artisan_id': artisan_id,
                    'assigned_by': request.user,
                    'status': 'PENDING',
                    'assigned_at': timezone.now(),
                }
            )
            print(f"🟢 Assignment {'created' if created else 'updated'} - ID: {assignment.id}")

            # Verify the artisan was correctly assigned
            if assignment.artisan_id != artisan_id:
                print("⚠️ Artisan mismatch, forcing update")
                assignment.artisan_id = artisan_id
                assignment.save(update_fields=['artisan_id'])

            return Response({
                'status': 'assigned',
                'assignment_id': str(assignment.id),
                'created': created,
            })

        except Exception as e:
            print(f"❌ Error creating/updating assignment: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Artisan accepts the assignment."""
        incident = self.get_object()
        if incident.assigned_to != request.user:
            return Response({'error': 'Not assigned to you'}, status=status.HTTP_403_FORBIDDEN)

        # Update the corresponding assignment
        assignment = getattr(incident, 'assignment', None)
        if assignment:
            assignment.accept()
        # You can add other status transition logic here if needed
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Artisan starts work (status = IN_PROGRESS)."""
        incident = self.get_object()
        if incident.assigned_to != request.user:
            return Response({'error': 'Not assigned to you'}, status=status.HTTP_403_FORBIDDEN)

        assignment = getattr(incident, 'assignment', None)
        if assignment:
            assignment.start()
        return Response({'status': 'started'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Artisan marks as completed."""
        incident = self.get_object()
        if incident.assigned_to != request.user:
            return Response({'error': 'Not assigned to you'}, status=status.HTTP_403_FORBIDDEN)

        assignment = getattr(incident, 'assignment', None)
        if assignment:
            assignment.complete()

        incident.resolved_at = timezone.now()
        incident.save(update_fields=['resolved_at'])
        return Response({'status': 'completed'})

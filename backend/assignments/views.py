from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Assignment
from .serializers import (
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentCreateUpdateSerializer,
)
from accounts.permissions import IsAdminOrStaff, IsDispatcher, IsArtisan


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('incident', 'artisan', 'assigned_by')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'artisan', 'incident']
    search_fields = ['incident__incident_number', 'artisan__email']
    ordering_fields = ['assigned_at', 'accepted_at', 'completed_at']
    ordering = ['-assigned_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return AssignmentListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return AssignmentCreateUpdateSerializer
        return AssignmentDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            self.permission_classes = [IsDispatcher | IsAdminOrStaff]
        elif self.action in ['destroy']:
            self.permission_classes = [IsAdminOrStaff]
        elif self.action in ['accept', 'reject', 'start', 'complete', 'my_assignments']:
            self.permission_classes = [IsArtisan]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=False, methods=['get'], url_path='my')
    def my_assignments(self, request):
        """Get all assignments for the authenticated artisan."""
        assignments = self.get_queryset().filter(artisan=request.user)
        serializer = AssignmentListSerializer(assignments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        assignment = self.get_object()
        if assignment.artisan != request.user:
            return Response({'error': 'Not assigned to you'}, status=status.HTTP_403_FORBIDDEN)
        if assignment.status != 'PENDING':
            return Response({'error': 'Assignment is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        assignment.accept()
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        assignment = self.get_object()
        if assignment.artisan != request.user:
            return Response({'error': 'Not assigned to you'}, status=status.HTTP_403_FORBIDDEN)
        if assignment.status != 'PENDING':
            return Response({'error': 'Assignment is not pending'}, status=status.HTTP_400_BAD_REQUEST)
        assignment.reject()
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        assignment = self.get_object()
        if assignment.artisan != request.user:
            return Response({'error': 'Not assigned to you'}, status=status.HTTP_403_FORBIDDEN)
        if assignment.status not in ['ACCEPTED']:
            return Response({'error': 'Assignment must be accepted first'}, status=status.HTTP_400_BAD_REQUEST)
        assignment.start()
        return Response({'status': 'in_progress'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        assignment = self.get_object()
        if assignment.artisan != request.user:
            return Response({'error': 'Not assigned to you'}, status=status.HTTP_403_FORBIDDEN)
        if assignment.status != 'IN_PROGRESS':
            return Response({'error': 'Assignment must be in progress'}, status=status.HTTP_400_BAD_REQUEST)
        assignment.complete()
        return Response({'status': 'completed'})

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from .models import CallLog
from .serializers import (
    CallLogListSerializer,
    CallLogDetailSerializer,
    CallLogCreateUpdateSerializer
)
from accounts.permissions import IsAdminOrStaff, IsAgent


class CallLogViewSet(viewsets.ModelViewSet):
    queryset = CallLog.objects.select_related('agent', 'customer', 'incident')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'agent', 'customer', 'incident', 'direction',
        'channel', 'status', 'disposition', 'follow_up_required'
    ]
    search_fields = ['reference', 'caller_number', 'notes', 'customer__name']
    ordering_fields = ['started_at', 'duration_seconds', 'created_at', 'follow_up_date']
    ordering = ['-started_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return CallLogListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return CallLogCreateUpdateSerializer
        return CallLogDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAgent | IsAdminOrStaff]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(agent=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=False, methods=['get'], url_path='my-calls')
    def my_calls(self, request):
        """Get calls handled by the current agent."""
        calls = self.get_queryset().filter(agent=request.user)
        serializer = CallLogListSerializer(calls, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='today')
    def today_calls(self, request):
        """Get calls made today."""
        today = timezone.now().date()
        calls = self.get_queryset().filter(started_at__date=today)
        serializer = CallLogListSerializer(calls, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='pending-followup')
    def pending_followup(self, request):
        """Get calls that need follow-up."""
        now = timezone.now()
        calls = self.get_queryset().filter(
            Q(follow_up_required=True) &
            Q(follow_up_date__lte=now) &
            Q(status=CallLog.Status.ACTIVE)
        )
        serializer = CallLogListSerializer(calls, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='end-call')
    def end_call(self, request, pk=None):
        """End the call (auto-calculates duration)."""
        call = self.get_object()
        if call.status != CallLog.Status.ACTIVE:
            return Response(
                {'error': 'Only active calls can be ended.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        call.end_call()
        return Response(CallLogDetailSerializer(call).data)

    @action(detail=True, methods=['post'], url_path='miss')
    def miss_call(self, request, pk=None):
        """Mark call as missed."""
        call = self.get_object()
        if call.status != CallLog.Status.ACTIVE:
            return Response(
                {'error': 'Only active calls can be marked missed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        call.mark_missed()
        return Response(CallLogDetailSerializer(call).data)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_call(self, request, pk=None):
        """Cancel the call."""
        call = self.get_object()
        if call.status in [CallLog.Status.COMPLETED, CallLog.Status.CANCELLED]:
            return Response(
                {'error': 'Cannot cancel an already completed or cancelled call.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        call.cancel()
        return Response(CallLogDetailSerializer(call).data)

    @action(detail=True, methods=['post'], url_path='schedule-followup')
    def schedule_followup(self, request, pk=None):
        """Set a follow-up date/time."""
        call = self.get_object()
        follow_up_date = request.data.get('follow_up_date')
        if not follow_up_date:
            return Response(
                {'error': 'follow_up_date is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            call.schedule_follow_up(follow_up_date)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(CallLogDetailSerializer(call).data)

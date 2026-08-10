# notifications/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Notification
from .serializers import (
    NotificationListSerializer,
    NotificationDetailSerializer,
    NotificationCreateSerializer,
)
from accounts.permissions import IsAdminOrStaff


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications.
    - Users see only their own notifications.
    - Admins/Staff see all notifications.
    - Create/Update/Delete are admin-only.
    - Mark as read, mark all read, and unread count are public actions.
    """
    queryset = Notification.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'is_read', 'notification_type', 'channel']
    search_fields = ['subject', 'message']
    ordering_fields = ['sent_at', 'is_read']
    ordering = ['-sent_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        if self.action == 'create':
            return NotificationCreateSerializer
        if self.action in ['update', 'partial_update']:
            return NotificationCreateSerializer
        return NotificationDetailSerializer

    def get_queryset(self):
        """
        Restrict notifications to the current user unless they are staff/admin.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Notification.objects.all()
        return Notification.objects.filter(user=user)

    def get_permissions(self):
        """
        Only admins/staff can create, update, or delete notifications.
        Everyone else can list, retrieve, mark read, etc.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrStaff]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    # ─── Custom Actions ───────────────────────────────────────

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark a single notification as read.
        Only the owner of the notification can mark it read.
        """
        notification = self.get_object()
        if notification.user != request.user:
            return Response(
                {'error': 'You do not have permission to mark this notification as read.'},
                status=status.HTTP_403_FORBIDDEN
            )
        notification.mark_as_read()
        return Response({
            'status': 'marked as read',
            'notification': NotificationDetailSerializer(notification).data
        })

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications for the current user as read.
        """
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({
            'status': f'{count} notifications marked as read',
            'count': count
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get the number of unread notifications for the current user.
        """
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'])
    def mark_unread(self, request, pk=None):
        """
        Mark a single notification as unread (optional).
        """
        notification = self.get_object()
        if notification.user != request.user:
            return Response(
                {'error': 'You do not have permission to modify this notification.'},
                status=status.HTTP_403_FORBIDDEN
            )
        notification.is_read = False
        notification.read_at = None
        notification.save(update_fields=['is_read', 'read_at'])
        return Response({
            'status': 'marked as unread',
            'notification': NotificationDetailSerializer(notification).data
        })

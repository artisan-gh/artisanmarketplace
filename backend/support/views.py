from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import SupportTicket, SupportReply
from .serializers import (
    SupportTicketSerializer,
    SupportTicketListSerializer,
    SupportReplySerializer,
    SupportReplyCreateSerializer,
    SupportTicketStatusUpdateSerializer,
)


class SupportTicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint for support tickets.
    """
    queryset = SupportTicket.objects.select_related('user', 'assigned_to').prefetch_related('replies').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'assigned_to', 'is_public']
    search_fields = ['subject', 'message']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(user=user, is_public=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return SupportTicketListSerializer
        return SupportTicketSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        """
        Add a reply to the ticket.
        """
        ticket = self.get_object()
        serializer = SupportReplyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reply = SupportReply.objects.create(
            ticket=ticket,
            responder=request.user,
            message=serializer.validated_data['message'],
            is_internal=serializer.validated_data.get('is_internal', False),
            attachment=serializer.validated_data.get('attachment')
        )

        # Update ticket status if user is staff and ticket is open
        if request.user.is_staff and ticket.status in [SupportTicket.Status.OPEN, SupportTicket.Status.IN_PROGRESS]:
            ticket.status = SupportTicket.Status.IN_PROGRESS
            ticket.save()

        return Response(SupportReplySerializer(reply).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the ticket status.
        """
        ticket = self.get_object()
        serializer = SupportTicketStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        # Only staff can change status
        if not request.user.is_staff:
            return Response({'error': 'Only support staff can change status.'}, status=status.HTTP_403_FORBIDDEN)

        if new_status == SupportTicket.Status.RESOLVED:
            ticket.resolve()
        elif new_status == SupportTicket.Status.CLOSED:
            ticket.close()
        elif new_status == SupportTicket.Status.OPEN:
            ticket.reopen()
        elif new_status == SupportTicket.Status.IN_PROGRESS:
            ticket.status = new_status
            ticket.save()
        else:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'updated', 'ticket': SupportTicketSerializer(ticket).data})

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign a staff member to the ticket.
        """
        ticket = self.get_object()
        if not request.user.is_staff:
            return Response({'error': 'Only support staff can assign tickets.'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        assignee = get_object_or_404(User, id=user_id, is_staff=True)
        ticket.assigned_to = assignee
        ticket.save()
        return Response({'status': 'assigned', 'assigned_to': assignee.email})

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """
        Get tickets for the current user.
        """
        tickets = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """
        Get unassigned tickets (staff only).
        """
        if not request.user.is_staff:
            return Response({'error': 'Only support staff can view unassigned tickets.'}, status=status.HTTP_403_FORBIDDEN)

        tickets = self.get_queryset().filter(assigned_to__isnull=True, status__in=[SupportTicket.Status.OPEN, SupportTicket.Status.IN_PROGRESS])
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

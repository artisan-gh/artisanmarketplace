from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import VerificationDocumentType, VerificationRequest
from .serializers import (
    VerificationDocumentTypeSerializer,
    VerificationRequestSerializer,
    VerificationRequestListSerializer,
    VerificationRequestCreateSerializer,
    VerificationRequestActionSerializer,
)


class VerificationDocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = VerificationDocumentType.objects.filter(is_active=True).all()
    serializer_class = VerificationDocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name']


class VerificationRequestViewSet(viewsets.ModelViewSet):
    queryset = VerificationRequest.objects.select_related('user', 'reviewed_by', 'document_type').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'document_type', 'user']
    search_fields = ['user__email', 'document_number', 'notes']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'list':
            return VerificationRequestListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return VerificationRequestCreateSerializer
        return VerificationRequestSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='action')
    def perform_action(self, request, pk=None):
        verification = self.get_object()
        serializer = VerificationRequestActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')

        if not request.user.is_staff:
            return Response({'error': 'Only staff can perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            if action_type == 'approve':
                verification.approve(request.user)
            elif action_type == 'reject':
                verification.reject(reason, request.user)
            elif action_type == 'start_review':
                verification.start_review()
            elif action_type == 'cancel':
                verification.cancel()
            elif action_type == 'expire':
                verification.expire()
            else:
                return Response({'error': 'Invalid action.'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({
                'status': 'success',
                'action': action_type,
                'verification': VerificationRequestSerializer(verification).data
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        qs = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Permission denied.'},
                            status=status.HTTP_403_FORBIDDEN)
        qs = self.get_queryset().filter(status=VerificationRequest.Status.PENDING)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get the current user's verification status summary."""
        user = request.user
        if hasattr(user, 'artisan_profile'):
            # Check if user has an approved verification
            approved = VerificationRequest.objects.filter(
                user=user,
                status=VerificationRequest.Status.APPROVED
            ).exists()
            return Response({
                'is_verified': approved,
                'has_pending': VerificationRequest.objects.filter(
                    user=user,
                    status=VerificationRequest.Status.PENDING
                ).exists()
            })
        return Response({'is_verified': False, 'has_pending': False})

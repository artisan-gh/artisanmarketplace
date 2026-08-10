from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from .models import AIModel, AIRequest
from .serializers import (
    AIModelSerializer,
    AIModelListSerializer,
    AIRequestSerializer,
    AIRequestCreateSerializer,
    AIRequestStatsSerializer,
)


class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_default', 'provider', 'model_type']
    search_fields = ['name', 'description', 'model_id']
    ordering_fields = ['name', 'created_at']
    ordering = ['-is_active', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return AIModelListSerializer
        return AIModelSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise permissions.PermissionDenied("Only staff can create AI models.")
        serializer.save()


class AIRequestViewSet(viewsets.ModelViewSet):
    queryset = AIRequest.objects.select_related('user', 'model').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['model', 'status', 'request_type', 'user']
    search_fields = ['request_id', 'error_message']
    ordering_fields = ['created_at', 'latency_ms', 'cost']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return AIRequestCreateSerializer
        return AIRequestSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        ai_request = self.get_object()
        if ai_request.status in ['success', 'failed', 'cancelled']:
            return Response({'error': 'Request already completed or cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        ai_request.cancel()
        return Response({'status': 'cancelled'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        stats = {
            'total_requests': qs.count(),
            'successful': qs.filter(status='success').count(),
            'failed': qs.filter(status='failed').count(),
            'pending': qs.filter(status__in=['pending', 'processing']).count(),
            'avg_latency': qs.filter(latency_ms__isnull=False).aggregate(Avg('latency_ms'))['latency_ms__avg'] or 0,
            'total_cost': qs.aggregate(Sum('cost'))['cost__sum'] or 0,
            'total_tokens': qs.aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0,
        }
        return Response(stats)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        qs = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

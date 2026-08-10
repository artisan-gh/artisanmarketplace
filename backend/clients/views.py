from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Client
from .serializers import (
    ClientSerializer,
    ClientListSerializer,
    ClientDetailSerializer,
)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = []
    search_fields = ['company_name', 'preferred_location', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['created_at', 'company_name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        if self.action == 'retrieve':
            return ClientDetailSerializer
        return ClientSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            client = request.user.client_profile
            serializer = self.get_serializer(client)
            return Response(serializer.data)
        except Client.DoesNotExist:
            return Response(
                {'detail': 'Client profile not found for this user.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_me(self, request):
        try:
            client = request.user.client_profile
            serializer = self.get_serializer(client, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Client.DoesNotExist:
            return Response(
                {'detail': 'Client profile not found for this user.'},
                status=status.HTTP_404_NOT_FOUND
            )

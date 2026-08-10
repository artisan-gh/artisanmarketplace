from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Location
from .serializers import (
    LocationSerializer,
    LocationListSerializer,
    LocationCreateSerializer,
    NearbyQuerySerializer,
)
from artisans.models import ArtisanProfile
from clients.models import Client

User = get_user_model()


class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user locations.
    """
    queryset = Location.objects.select_related('user').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['city', 'region', 'formatted_address']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return LocationListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return LocationCreateSerializer
        return LocationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=False, methods=['get'])
    def my_location(self, request):
        try:
            location = Location.objects.get(user=request.user)
            serializer = self.get_serializer(location)
            return Response(serializer.data)
        except Location.DoesNotExist:
            return Response({'detail': 'Location not set.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def nearby_artisans(self, request):
        """
        Find artisans within a radius.
        """
        serializer = NearbyQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lat = serializer.validated_data['latitude']
        lon = serializer.validated_data['longitude']
        radius = serializer.validated_data['radius_km']

        # Get all artisans with locations
        artisan_user_ids = Artisan.objects.values_list('user_id', flat=True)
        locations = Location.objects.filter(user_id__in=artisan_user_ids)

        # Filter by distance (client-side or use raw SQL / PostGIS)
        nearby = []
        for loc in locations:
            distance = loc.distance_to(lat, lon)
            if distance <= radius:
                nearby.append({
                    'artisan_id': loc.user.artisan_profile.id,
                    'business_name': loc.user.artisan_profile.business_name,
                    'distance_km': round(distance, 2),
                    'location': LocationListSerializer(loc).data,
                })

        nearby.sort(key=lambda x: x['distance_km'])
        return Response(nearby)

    @action(detail=False, methods=['post'])
    def nearby_clients(self, request):
        # Similar to nearby_artisans but for clients
        pass

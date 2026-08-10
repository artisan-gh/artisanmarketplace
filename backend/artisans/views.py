# artisan/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import ArtisanProfile, Skill, ArtisanAvailability
from .serializers import (
    ArtisanProfileListSerializer,
    ArtisanProfileDetailSerializer,
    ArtisanProfileCreateUpdateSerializer,
    SkillSerializer,
    ArtisanAvailabilitySerializer,
    ArtisanAvailabilityCreateUpdateSerializer,
)
from accounts.permissions import IsAdminOrStaff, IsDispatcher, IsArtisan


# ─── Skill ViewSet (legacy) ──────────────────────────────────
class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.filter(is_active=True)
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrStaff]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


# ─── ArtisanProfile ViewSet ───────────────────────────────────
class ArtisanProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Artisan Profiles.
    Includes filtering by category, skills, and availability.
    """
    queryset = ArtisanProfile.objects.select_related('user', 'category').prefetch_related(
        'skills', 'legacy_skills', 'availability'
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_available', 'skills', 'category']  # ✅ added category filter
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['average_rating', 'user__first_name', 'hire_date']
    ordering = ['user__first_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ArtisanProfileListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ArtisanProfileCreateUpdateSerializer
        if self.action == 'my_profile':
            return ArtisanProfileDetailSerializer
        return ArtisanProfileDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrStaff]
        elif self.action == 'set_availability':
            self.permission_classes = [IsArtisan]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get the authenticated artisan's profile."""
        try:
            profile = request.user.artisan_profile
        except ArtisanProfile.DoesNotExist:
            return Response({'error': 'No artisan profile found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ArtisanProfileDetailSerializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='available')
    def available_artisans(self, request):
        """List all available artisans."""
        queryset = self.get_queryset().filter(is_available=True)
        serializer = ArtisanProfileListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='availability')
    def get_availability(self, request, pk=None):
        """Get the full availability schedule for an artisan."""
        profile = self.get_object()
        avail = profile.availability.all()
        serializer = ArtisanAvailabilitySerializer(avail, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='availability')
    def set_availability(self, request, pk=None):
        """
        Add or update a single day's availability for the artisan.
        Only the artisan themselves or staff can modify.
        """
        profile = self.get_object()
        if profile.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Cannot modify another artisan\'s availability'},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data
        day = data.get('day_of_week')
        start = data.get('start_time')
        end = data.get('end_time')
        is_working = data.get('is_working', True)

        if day is None:
            return Response(
                {'error': 'day_of_week is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        availability, created = ArtisanAvailability.objects.update_or_create(
            artisan=profile,
            day_of_week=day,
            defaults={'start_time': start, 'end_time': end, 'is_working': is_working}
        )
        serializer = ArtisanAvailabilitySerializer(availability)
        return Response(serializer.data, status=status.HTTP_200_OK)
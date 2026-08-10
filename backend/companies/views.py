from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Company
from .serializers import (
    CompanySerializer,
    CompanyListSerializer,
    CompanyCreateSerializer,
    CompanyUpdateSerializer,
)
from organizations.models import OrganizationMember


class CompanyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for companies.
    """
    queryset = Company.objects.prefetch_related('members').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_verified']
    search_fields = ['name', 'registration_number', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        # Users see companies they own or are a member of
        member_companies = OrganizationMember.objects.filter(user=user).values_list('company_id', flat=True)
        return self.queryset.filter(
            models.Q(owner=user) | models.Q(id__in=member_companies)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        if self.action == 'create':
            return CompanyCreateSerializer
        if self.action in ['update', 'partial_update']:
            return CompanyUpdateSerializer
        return CompanySerializer

    def perform_create(self, serializer):
        company = serializer.save(owner=self.request.user)
        # Add owner as an OWNER member
        OrganizationMember.objects.create(
            company=company,
            user=self.request.user,
            role=OrganizationMember.Role.OWNER
        )

    def perform_update(self, serializer):
        # Ensure the user has permission (owner or admin)
        company = self.get_object()
        if not company.can_manage(self.request.user):
            raise permissions.PermissionDenied("You do not have permission to edit this company.")
        serializer.save()

    def perform_destroy(self, instance):
        if not instance.can_manage(self.request.user):
            raise permissions.PermissionDenied("You do not have permission to delete this company.")
        instance.delete()

    # ─── Custom Actions ──────────────────────────────────────

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        company = self.get_object()
        members = company.members.select_related('user').all()
        from organizations.serializers import OrganizationMemberListSerializer
        serializer = OrganizationMemberListSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_companies(self, request):
        """Get companies owned by or belonging to the current user."""
        qs = self.get_queryset().filter(
            models.Q(owner=request.user) | models.Q(members__user=request.user)
        ).distinct()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        company = self.get_object()
        if not company.can_manage(request.user):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        role = request.data.get('role', OrganizationMember.Role.MEMBER)
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        from accounts.models import User
        user = get_object_or_404(User, id=user_id)
        if OrganizationMember.objects.filter(company=company, user=user).exists():
            return Response({'error': 'User is already a member.'}, status=status.HTTP_400_BAD_REQUEST)
        membership = OrganizationMember.objects.create(
            company=company,
            user=user,
            role=role
        )
        from organizations.serializers import OrganizationMemberSerializer
        return Response(OrganizationMemberSerializer(membership).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        company = self.get_object()
        if not company.can_manage(request.user):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        membership = get_object_or_404(OrganizationMember, company=company, user_id=user_id)
        if membership.role == OrganizationMember.Role.OWNER:
            return Response({'error': 'Cannot remove the owner.'}, status=status.HTTP_400_BAD_REQUEST)
        membership.delete()
        return Response({'status': 'removed'})

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Organization, OrganizationMember, OrganizationInvite
from .serializers import (
    OrganizationListSerializer,
    OrganizationDetailSerializer,
    OrganizationCreateUpdateSerializer,
    OrganizationMemberSerializer,
    OrganizationMemberCreateSerializer,
    OrganizationInviteSerializer,
    OrganizationInviteCreateSerializer,
)
from accounts.permissions import IsAdminOrStaff, IsAdmin, IsManager, IsSupervisor


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Organization CRUD.
    - Admins/Staff: full access
    - Managers/Supervisors: can view only
    - Others: no access
    """
    queryset = Organization.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "email", "phone", "tax_id"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "list":
            return OrganizationListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return OrganizationCreateUpdateSerializer
        return OrganizationDetailSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminOrStaff]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=["get"], url_path="members")
    def members(self, request, pk=None):
        """List all members of an organization."""
        organization = self.get_object()
        members = organization.members.filter(is_active=True)
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="members/add")
    def add_member(self, request, pk=None):
        """Add a member to the organization."""
        organization = self.get_object()
        serializer = OrganizationMemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(organization=organization)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="invites")
    def invites(self, request, pk=None):
        """List all invites for an organization."""
        organization = self.get_object()
        invites = organization.invites.filter(status=OrganizationInvite.Status.PENDING)
        serializer = OrganizationInviteSerializer(invites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="invites/create")
    def create_invite(self, request, pk=None):
        """Create an invite for a user to join the organization."""
        organization = self.get_object()
        serializer = OrganizationInviteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite = serializer.save(
            organization=organization,
            invited_by=request.user
        )
        return Response(
            OrganizationInviteSerializer(invite).data,
            status=status.HTTP_201_CREATED
        )


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organization members.
    """
    queryset = OrganizationMember.objects.filter(is_active=True)
    serializer_class = OrganizationMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["organization", "role", "is_active"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]

    def get_permissions(self):
        if self.action in ["destroy"]:
            self.permission_classes = [IsAdminOrStaff]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class OrganizationInviteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organization invites.
    """
    queryset = OrganizationInvite.objects.all()
    serializer_class = OrganizationInviteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["organization", "status", "email"]
    search_fields = ["email"]

    @action(detail=True, methods=["post"], url_path="accept")
    def accept_invite(self, request, pk=None):
        """Accept an invite (requires authentication)."""
        invite = self.get_object()
        try:
            invite.accept(request.user)
            return Response({"status": "Invite accepted"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject_invite(self, request, pk=None):
        """Reject an invite."""
        invite = self.get_object()
        try:
            invite.reject()
            return Response({"status": "Invite rejected"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

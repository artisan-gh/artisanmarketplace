from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.models import TimeStampedModel


class Organization(TimeStampedModel):
    """
    Company/Organization model – B2B clients.
    """
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True, help_text="Tax/VAT ID")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


class OrganizationMember(TimeStampedModel):
    """
    A user's membership in an organization with a specific role.
    """

    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        MEMBER = 'MEMBER', 'Member'
        VIEWER = 'VIEWER', 'Viewer'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        help_text="The role of the user within the organization"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this membership is currently active"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['organization', 'role', 'user__email']
        unique_together = ['organization', 'user']
        indexes = [
            models.Index(fields=['organization', 'role']),
            models.Index(fields=['user', 'role']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = "Organization Member"
        verbose_name_plural = "Organization Members"

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.get_role_display()})"

    @property
    def is_owner(self):
        return self.role == self.Role.OWNER

    @property
    def is_admin(self):
        return self.role in [self.Role.OWNER, self.Role.ADMIN]

    @property
    def can_manage_members(self):
        return self.role in [self.Role.OWNER, self.Role.ADMIN, self.Role.MANAGER]


class OrganizationInvite(TimeStampedModel):
    """
    Invitation to join an organization.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invites',
        null=True,          # <-- add this
        blank=True,         # <-- add this
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_organization_invites'
    )

    email = models.EmailField(help_text="Email of the invited user")
    role = models.CharField(
        max_length=20,
        choices=OrganizationMember.Role.choices,
        default=OrganizationMember.Role.MEMBER
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )

    token = models.CharField(max_length=64, unique=True, blank=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['token']),
        ]
        verbose_name = "Organization Invite"
        verbose_name_plural = "Organization Invites"

    def __str__(self):
        return f"Invite {self.email} to {self.organization.name}"

    def save(self, *args, **kwargs):
        import secrets
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def accept(self, user):
        if self.status != self.Status.PENDING:
            raise ValidationError("Invite is not pending.")
        if self.is_expired:
            self.status = self.Status.EXPIRED
            self.save()
            raise ValidationError("Invite has expired.")
        OrganizationMember.objects.create(
            organization=self.organization,
            user=user,
            role=self.role
        )
        self.status = self.Status.ACCEPTED
        self.accepted_at = timezone.now()
        self.save()
        return user

    def reject(self):
        if self.status != self.Status.PENDING:
            raise ValidationError("Invite is not pending.")
        self.status = self.Status.REJECTED
        self.save()

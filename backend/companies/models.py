from django.db import models
from django.conf import settings
from django.utils.text import slugify
from common.models import TimeStampedModel


class Company(TimeStampedModel):
    """
    A company/organization that can have members and manage services.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies"
    )

    name = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)

    registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official business registration number"
    )

    description = models.TextField(blank=True)

    logo = models.ImageField(
        upload_to="companies/",
        blank=True,
        null=True
    )

    # ─── Contact Information ──────────────────────────────────
    email = models.EmailField(blank=True, help_text="Company contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Company phone number")
    website = models.URLField(blank=True, help_text="Company website")
    address = models.TextField(blank=True, help_text="Physical address")

    # ─── Status ───────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the company is currently active"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the company has been verified"
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_verified']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    # ─── Member Management ────────────────────────────────────

    @property
    def members_count(self):
        """Total number of active members in the company."""
        return self.members.filter(is_active=True).count()

    @property
    def admins(self):
        """Get all admin-level members (OWNER, ADMIN)."""
        from organizations.models import OrganizationMember
        return OrganizationMember.objects.filter(
            company=self,
            role__in=[OrganizationMember.Role.OWNER, OrganizationMember.Role.ADMIN],
            is_active=True
        )

    @property
    def is_owner(self, user):
        """Check if a user is the owner of this company."""
        return self.owner == user

    def has_member(self, user):
        """Check if a user is a member of this company."""
        from organizations.models import OrganizationMember
        return OrganizationMember.objects.filter(company=self, user=user).exists()

    def get_member_role(self, user):
        """Get the role of a user in this company, or None if not a member."""
        from organizations.models import OrganizationMember
        try:
            return OrganizationMember.objects.get(company=self, user=user).role
        except OrganizationMember.DoesNotExist:
            return None

    def can_manage(self, user):
        """Check if a user can manage this company (owner or admin)."""
        role = self.get_member_role(user)
        if role in ['OWNER', 'ADMIN']:
            return True
        return user == self.owner

    def can_invite(self, user):
        """Check if a user can invite others to this company."""
        role = self.get_member_role(user)
        if role in ['OWNER', 'ADMIN', 'MANAGER']:
            return True
        return user == self.owner

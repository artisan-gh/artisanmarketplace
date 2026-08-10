from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class BaseModel(models.Model):
    """
    Abstract base model with common fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated"
    )
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])


class Customer(BaseModel):
    """
    Customer model – individuals or companies who call in with issues.
    """
    name = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True, db_index=True)
    address = models.TextField(blank=True)
    gps_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Latitude from GPS"
    )
    gps_lng = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Longitude from GPS"
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        help_text="If this customer belongs to a company/organization"
    )
    notes = models.TextField(blank=True, help_text="Internal notes about this customer")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name", "phone"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone})"

    def get_full_address(self):
        parts = [self.address]
        if self.gps_lat and self.gps_lng:
            parts.append(f"GPS: {self.gps_lat}, {self.gps_lng}")
        return ", ".join(filter(None, parts))

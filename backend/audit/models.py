# audit/models.py
import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .managers import AuditLogManager
from .choices import AuditAction, AuditSeverity, HttpMethod


class AuditLog(models.Model):
    """
    Enterprise‑grade audit log – lean model, business logic in AuditService.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the audit log entry"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
        db_comment="User who performed the action",
        help_text="User who performed the action"
    )

    action = models.CharField(
        max_length=20,
        choices=AuditAction.choices,
        db_index=True,
        db_comment="Type of action performed",
        help_text="The action performed by the user"
    )
    severity = models.CharField(
        max_length=10,
        choices=AuditSeverity.choices,
        default=AuditSeverity.LOW,
        db_comment="How critical this action is",
        help_text="How critical this action is"
    )
    module = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        db_comment="App/module name (e.g., 'incidents')",
        help_text="App/module name (e.g., 'incidents')"
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Content type of the logged object"
    )
    object_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Primary key of the logged object"
    )
    content_object = GenericForeignKey("content_type", "object_id")
    object_repr = models.CharField(
        max_length=500,
        blank=True,
        db_comment="String representation of the object",
        help_text="String representation of the object"
    )

    old_values = models.JSONField(
        null=True,
        blank=True,
        db_comment="Previous values (before action)",
        help_text="Previous values (before action)"
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        db_comment="New values (after action)",
        help_text="New values (after action)"
    )

    success = models.BooleanField(
        default=True,
        db_index=True,
        db_comment="Whether the operation succeeded",
        help_text="Whether the operation succeeded"
    )
    response_status = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_comment="HTTP status code",
        help_text="HTTP status code"
    )
    duration_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_comment="Execution time in milliseconds",
        help_text="Execution time in milliseconds"
    )

    request_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        db_comment="Unique ID of the request",
        help_text="Unique ID of the request"
    )
    correlation_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,           # ✅ Added null=True to allow NULL in database
        db_index=True,
        db_comment="ID linking multiple requests in a workflow",
        help_text="ID linking multiple requests in a workflow"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_comment="Client IP (with proxy support)",
        help_text="Client IP (with proxy support)"
    )
    path = models.CharField(
        max_length=255,
        blank=True,
        db_comment="Request path",
        help_text="Request path"
    )
    method = models.CharField(
        max_length=10,
        choices=HttpMethod.choices,
        blank=True,
        db_comment="HTTP method",
        help_text="HTTP method"
    )

    user_agent = models.TextField(
        blank=True,
        help_text="Raw user agent string"
    )
    browser = models.CharField(
        max_length=50,
        blank=True,
        db_comment="Browser family (parsed)",
        help_text="Browser family (parsed)"
    )
    operating_system = models.CharField(
        max_length=50,
        blank=True,
        db_comment="OS family (parsed)",
        help_text="OS family (parsed)"
    )
    device = models.CharField(
        max_length=50,
        blank=True,
        db_comment="Device family (parsed)",
        help_text="Device family (parsed)"
    )

    description = models.TextField(
        blank=True,
        db_comment="Human‑readable description of the event",
        help_text="Human‑readable description of the event"
    )
    exception = models.TextField(
        blank=True,
        db_comment="Exception traceback (if any)",
        help_text="Exception traceback (if any)"
    )
    archived = models.BooleanField(
        default=False,
        db_index=True,
        db_comment="Whether this log entry has been archived",
        help_text="Whether this log entry has been archived"
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        db_comment="For multi‑tenant support",
        help_text="For multi‑tenant support"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the log entry was created"
    )

    objects = AuditLogManager()

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["module", "created_at"]),
            models.Index(fields=["action", "module"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["request_id"]),
            models.Index(fields=["correlation_id"]),
            models.Index(fields=["organization"]),
            models.Index(fields=["severity", "created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(duration_ms__isnull=True) |
                    models.Q(duration_ms__gte=0)
                ),
                name="audit_duration_positive",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(response_status__isnull=True) |
                    (
                        models.Q(response_status__gte=100) &
                        models.Q(response_status__lte=599)
                    )
                ),
                name="audit_http_status_valid",
            ),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action} {self.module or 'system'}"

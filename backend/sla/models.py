import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class SLAPolicy(models.Model):
    """
    Service Level Agreement policy.
    Defines resolution targets per priority/category.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    priority = models.CharField(
        max_length=20,
        choices=(
            ('LOW', 'Low'),
            ('MEDIUM', 'Medium'),
            ('HIGH', 'High'),
            ('CRITICAL', 'Critical'),
        ),
        blank=True,
        null=True,
        help_text="If set, applies only to this priority"
    )
    category = models.ForeignKey(
        'incident_category.IncidentCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="If set, applies only to this category"
    )

    response_hours = models.PositiveIntegerField(default=1)
    resolution_hours = models.PositiveIntegerField(default=24)

    escalation_after_hours = models.PositiveIntegerField(null=True, blank=True)
    escalation_target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sla_escalations'
    )

    business_hours_only = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', 'name']
        verbose_name = "SLA Policy"
        verbose_name_plural = "SLA Policies"

    def __str__(self):
        parts = [self.name]
        if self.priority:
            parts.append(f"({self.priority})")
        return " ".join(parts)

    def clean(self):
        if self.escalation_after_hours and self.escalation_after_hours >= self.resolution_hours:
            raise ValidationError("Escalation time must be less than resolution time.")


class SLATracker(models.Model):
    """
    Tracks SLA for each incident.
    """
    STATUS_CHOICES = (
        ('ON_TRACK', 'On Track'),
        ('AT_RISK', 'At Risk'),
        ('BREACHED', 'Breached'),
        ('RESOLVED', 'Resolved'),
        ('ESCALATED', 'Escalated'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.OneToOneField(
        'incidents.Incident',
        on_delete=models.CASCADE,
        related_name='sla_tracker'
    )
    policy = models.ForeignKey(SLAPolicy, on_delete=models.PROTECT)

    target_response = models.DateTimeField()
    target_resolution = models.DateTimeField()
    target_escalation = models.DateTimeField(null=True, blank=True)

    response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    escalated_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ON_TRACK'
    )

    breach_reason = models.TextField(blank=True)
    escalated_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sla_escalated_incidents'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['incident']),
            models.Index(fields=['status']),
            models.Index(fields=['target_resolution']),
            models.Index(fields=['target_escalation']),
        ]
        verbose_name = "SLA Tracker"
        verbose_name_plural = "SLA Trackers"

    def __str__(self):
        return f"SLA for {self.incident.incident_number} - {self.status}"

    @property
    def is_breached(self):
        return self.status == 'BREACHED'

    @property
    def time_remaining(self):
        if self.status in ['RESOLVED', 'BREACHED']:
            return None
        remaining = self.target_resolution - timezone.now()
        return remaining.total_seconds() / 3600

    def check_status(self):
        now = timezone.now()
        if self.resolved_at:
            self.status = 'RESOLVED'
        elif self.target_resolution < now:
            self.status = 'BREACHED'
            self.breach_reason = f"Resolution time exceeded by {(now - self.target_resolution).total_seconds() / 3600:.1f} hours"
        elif self.target_escalation and self.target_escalation < now:
            self.status = 'ESCALATED'
        elif self.target_resolution < now + timezone.timedelta(hours=4):
            self.status = 'AT_RISK'
        else:
            self.status = 'ON_TRACK'
        self.save()

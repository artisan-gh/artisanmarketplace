from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.models import TimeStampedModel


class SupportTicket(TimeStampedModel):
    """
    A customer support ticket.
    """

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Category(models.TextChoices):
        GENERAL = 'GENERAL', 'General Inquiry'
        BOOKING = 'BOOKING', 'Booking Issue'
        PAYMENT = 'PAYMENT', 'Payment Issue'
        TECHNICAL = 'TECHNICAL', 'Technical Problem'
        ACCOUNT = 'ACCOUNT', 'Account Issue'
        FEATURE = 'FEATURE', 'Feature Request'
        OTHER = 'OTHER', 'Other'

    # ─── Relations ────────────────────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        help_text="Support staff assigned to this ticket"
    )

    # ─── Content ──────────────────────────────────────────────
    subject = models.CharField(max_length=200)
    message = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    # ─── Status ──────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )

    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # ─── Metadata ─────────────────────────────────────────────
    is_public = models.BooleanField(
        default=True,
        help_text="Whether the ticket is visible to the user"
    )

    attachment = models.FileField(
        upload_to='support_attachments/%Y/%m/%d/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['priority']),
            models.Index(fields=['created_at']),
        ]
        verbose_name_plural = "Support Tickets"

    def __str__(self):
        return f"{self.subject} - {self.user.email}"

    # ─── Status methods ──────────────────────────────────────

    def resolve(self):
        if self.status not in [self.Status.OPEN, self.Status.IN_PROGRESS]:
            raise ValueError("Only open or in-progress tickets can be resolved.")
        self.status = self.Status.RESOLVED
        self.resolved_at = timezone.now()
        self.save()

    def close(self):
        if self.status == self.Status.CLOSED:
            raise ValueError("Ticket is already closed.")
        self.status = self.Status.CLOSED
        self.closed_at = timezone.now()
        self.save()

    def reopen(self):
        if self.status == self.Status.CLOSED:
            self.status = self.Status.OPEN
            self.closed_at = None
            self.save()
        else:
            raise ValueError("Only closed tickets can be reopened.")


class SupportReply(TimeStampedModel):
    """
    A reply to a support ticket.
    """
    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_replies'
    )

    message = models.TextField()

    is_internal = models.BooleanField(
        default=False,
        help_text="If true, only support staff can see this reply"
    )

    attachment = models.FileField(
        upload_to='support_replies/%Y/%m/%d/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply to {self.ticket.subject[:30]}"

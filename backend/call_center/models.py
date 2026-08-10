import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CallLog(TimeStampedModel):
    """
    Manual Call Log.

    Designed for organizations where agents receive calls on ordinary
    mobile phones. It records the communication only; incident resolution
    is managed in the Incident module.
    """

    class Direction(models.TextChoices):
        INBOUND = "INBOUND", "Inbound"
        OUTBOUND = "OUTBOUND", "Outbound"

    class Channel(models.TextChoices):
        PHONE = "PHONE", "Phone"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        SMS = "SMS", "SMS"
        EMAIL = "EMAIL", "Email"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        MISSED = "MISSED", "Missed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Disposition(models.TextChoices):
        INCIDENT_CREATED = "INCIDENT_CREATED", "Incident Created"
        INCIDENT_UPDATED = "INCIDENT_UPDATED", "Incident Updated"
        INFORMATION_PROVIDED = "INFORMATION_PROVIDED", "Information Provided"
        FOLLOW_UP_REQUIRED = "FOLLOW_UP_REQUIRED", "Follow-up Required"
        NO_ACTION = "NO_ACTION", "No Action"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    reference = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="call_logs"
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="call_logs"
    )

    incident = models.ForeignKey(
        "incidents.Incident",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="call_logs"
    )

    direction = models.CharField(
        max_length=10,
        choices=Direction.choices,
        default=Direction.INBOUND,
        db_index=True
    )

    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.PHONE
    )

    caller_number = models.CharField(max_length=20)

    started_at = models.DateTimeField(default=timezone.now)

    ended_at = models.DateTimeField(
        null=True,
        blank=True
    )

    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    disposition = models.CharField(
        max_length=30,
        choices=Disposition.choices,
        default=Disposition.INCIDENT_CREATED,
        db_index=True
    )

    notes = models.TextField(blank=True)

    follow_up_required = models.BooleanField(default=False)

    follow_up_date = models.DateTimeField(
        null=True,
        blank=True
    )

    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Call Log"
        verbose_name_plural = "Call Logs"

        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["agent", "started_at"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["incident"]),
            models.Index(fields=["status"]),
            models.Index(fields=["direction"]),
            models.Index(fields=["disposition"]),
        ]

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()

        if self.started_at and self.ended_at:
            self.duration_seconds = max(
                0,
                int((self.ended_at - self.started_at).total_seconds())
            )

        super().save(*args, **kwargs)

    def generate_reference(self):
        year = timezone.now().year

        last = (
            CallLog.objects
            .filter(reference__startswith=f"CALL-{year}-")
            .order_by("-reference")
            .first()
        )

        seq = 1

        if last:
            try:
                seq = int(last.reference.split("-")[-1]) + 1
            except Exception:
                pass

        return f"CALL-{year}-{seq:06d}"

    def end_call(self):
        self.ended_at = timezone.now()
        self.status = self.Status.COMPLETED
        self.save(update_fields=[
            "ended_at",
            "status",
            "duration_seconds",
            "updated_at",
        ])

    def mark_missed(self):
        self.status = self.Status.MISSED
        self.ended_at = timezone.now()
        self.save(update_fields=[
            "status",
            "ended_at",
            "updated_at",
        ])

    def cancel(self):
        self.status = self.Status.CANCELLED
        self.save(update_fields=[
            "status",
            "updated_at",
        ])

    def schedule_follow_up(self, date):
        self.follow_up_required = True
        self.follow_up_date = date
        self.disposition = self.Disposition.FOLLOW_UP_REQUIRED
        self.save(update_fields=[
            "follow_up_required",
            "follow_up_date",
            "disposition",
            "updated_at",
        ])

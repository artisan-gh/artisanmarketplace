# notifications/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid


class Notification(models.Model):
    """
    Real‑time notification model with multi‑channel support.
    """

    class NotificationType(models.TextChoices):
        ASSIGNMENT = 'ASSIGNMENT', 'Assignment'
        STATUS_UPDATE = 'STATUS_UPDATE', 'Status Update'
        ESCALATION = 'ESCALATION', 'Escalation'
        REMINDER = 'REMINDER', 'Reminder'
        INCIDENT_CREATED = 'INCIDENT_CREATED', 'Incident Created'
        SLA_BREACHED = 'SLA_BREACHED', 'SLA Breached'
        PAYMENT_RECEIVED = 'PAYMENT_RECEIVED', 'Payment Received'
        INVOICE_SENT = 'INVOICE_SENT', 'Invoice Sent'
        GENERAL = 'GENERAL', 'General'

    class Channel(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        PUSH = 'PUSH', 'Push'
        IN_APP = 'IN_APP', 'In-App'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    incident = models.ForeignKey('incidents.Incident', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    assignment = models.ForeignKey('assignments.Assignment', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.GENERAL)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.IN_APP)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True, help_text="Extra metadata (e.g., incident_id, assignment_id)")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['sent_at']),
        ]
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        return f"{self.user.email} - {self.subject[:30]}"

    def mark_as_read(self):
        """Mark this notification as read."""
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])

    @classmethod
    def create_notification(cls, user, notification_type, subject, message, data=None, channel=Channel.IN_APP):
        """
        Create a notification and deliver it via the specified channel(s).
        - For IN_APP: broadcast via WebSocket.
        - For EMAIL/SMS: send via Celery (async).
        """
        # ─── 1. Create the notification record ──────────────
        notification = cls.objects.create(
            user=user,
            notification_type=notification_type,
            subject=subject,
            message=message,
            data=data or {},
            channel=channel,
        )

        # ─── 2. Deliver via selected channel ──────────────────
        if channel == cls.Channel.IN_APP:
            cls._broadcast_websocket(notification)
        elif channel == cls.Channel.EMAIL:
            cls._send_email(notification)
        elif channel == cls.Channel.SMS:
            cls._send_sms(notification)

        return notification

    # ─── Channel delivery methods ────────────────────────────

    @staticmethod
    def _broadcast_websocket(notification):
        """Broadcast notification to the user's WebSocket group."""
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{notification.user.id}",
            {
                "type": "send_notification",
                "data": {
                    "id": str(notification.id),
                    "type": notification.notification_type,
                    "subject": notification.subject,
                    "message": notification.message,
                    "data": notification.data,
                    "is_read": notification.is_read,
                    "created_at": notification.sent_at.isoformat(),
                }
            }
        )

    @staticmethod
    def _send_email(notification):
        """Send email asynchronously via Celery."""
        try:
            from notifications.tasks import send_email_notification
            send_email_notification.delay(
                user_id=notification.user.id,
                subject=notification.subject,
                message=notification.message,
            )
        except ImportError:
            # Fallback: send synchronously (not recommended for production)
            from django.core.mail import send_mail
            send_mail(
                subject=notification.subject,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                fail_silently=True,
            )

    @staticmethod
    def _send_sms(notification):
        """Send SMS asynchronously via Celery."""
        try:
            from notifications.tasks import send_sms_notification
            send_sms_notification.delay(
                user_id=notification.user.id,
                message=notification.message,
            )
        except ImportError:
            # SMS fallback – log only
            import logging
            logging.warning(f"SMS not sent to {notification.user.phone_number}: {notification.message}")

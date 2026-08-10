# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    """
    When a notification is created, broadcast it via WebSocket
    only if the channel is 'IN_APP'.
    Email/SMS notifications are handled separately.
    """
    if created and instance.channel == Notification.Channel.IN_APP:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.user.id}",
            {
                "type": "send_notification",
                "data": {
                    "id": str(instance.id),
                    "type": instance.notification_type,
                    "subject": instance.subject,
                    "message": instance.message,
                    "data": instance.data,
                    "is_read": instance.is_read,
                    "created_at": instance.sent_at.isoformat(),
                }
            }
        )
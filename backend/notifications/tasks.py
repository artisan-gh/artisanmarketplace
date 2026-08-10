# notifications/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings
from .models import Notification
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification_task(user_id, subject, message, channel='email', notification_type='SYSTEM', related_data=None):
    """
    Celery task to send a notification via email/SMS and create an in-app notification.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found. Notification not sent.")
        return

    recipient = getattr(user, 'email', None)
    phone_number = getattr(user, 'phone_number', None)

    # 1. Send via channel
    if channel == 'email':
        if not recipient:
            logger.warning(f"User {user_id} has no email address.")
            return
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            logger.info(f"Email sent to {recipient}")
        except Exception as e:
            logger.error(f"Email failed: {e}")

    elif channel == 'sms':
        if not phone_number:
            logger.warning(f"User {user_id} has no phone number.")
            return

        # ─── Format phone number for Ghana ──────────────────
        if phone_number:
            # If number starts with 0 and has 9–10 digits, assume Ghana
            if phone_number.startswith('0') and len(phone_number) >= 9:
                phone_number = '+233' + phone_number[1:]
            # If it's already in +233 format, keep it
            # If it's missing the +, add it
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message[:160],
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            logger.info(f"SMS sent to {phone_number}")
        except Exception as e:
            logger.error(f"SMS failed: {e}")

    # 2. Create in-app notification
    try:
        Notification.objects.create(
            user=user,
            subject=subject,
            message=message,
            notification_type=notification_type,
            channel=Notification.Channel.IN_APP,
            sent_at=timezone.now(),
            is_read=False,
            read_at=None,
            data=related_data or {},
        )
        logger.info(f"In-app notification created for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to create in-app notification: {e}")
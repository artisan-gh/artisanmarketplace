
"""SMS sender. Dev: console. Prod: Hubtel (set SMS_BACKEND=hubtel)."""
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def _send_console(phone, message):
    print(f"\n[SMS → {phone}]\n{message}\n")
    return True


def _send_hubtel(phone, message):
    try:
        import requests
    except ImportError:
        logger.error("requests not installed; cannot send SMS")
        return False
    try:
        r = requests.get(
            "https://smsc.hubtel.com/v1/messages/send",
            params={
                "clientid": settings.HUBTEL_CLIENT_ID,
                "clientsecret": settings.HUBTEL_CLIENT_SECRET,
                "from": settings.HUBTEL_SENDER_ID,
                "to": phone,
                "content": message,
            },
            timeout=15,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        logger.exception("Hubtel SMS failed: %s", e)
        return False


BACKENDS = {"console": _send_console, "hubtel": _send_hubtel}


def send_sms(phone, message):
    backend = BACKENDS.get(getattr(settings, "SMS_BACKEND", "console"), _send_console)
    return backend(phone, message)


def send_otp_sms(phone, code):
    return send_sms(phone, f"Your Tumakonect verification code is {code}. Valid for 5 minutes.")

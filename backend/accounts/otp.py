
"""OTP issue + verify + rate limits."""
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .models import OTPCode

OTP_TTL = getattr(settings, "OTP_TTL_SECONDS", 300)
OTP_MAX_ATTEMPTS = getattr(settings, "OTP_MAX_ATTEMPTS", 3)
OTP_MAX_PER_HOUR = getattr(settings, "OTP_MAX_PER_HOUR", 5)
OTP_MAX_PER_HOUR_PER_IP = getattr(settings, "OTP_MAX_PER_HOUR_PER_IP", 20)


def _rate_key_phone(phone): return f"otp:rate:phone:{phone}"
def _rate_key_ip(ip): return f"otp:rate:ip:{ip}" if ip else None


def _check_rate_limit(phone, ip):
    if cache.get(_rate_key_phone(phone), 0) >= OTP_MAX_PER_HOUR:
        raise ValueError("Too many codes requested for this number. Try again later.")
    ip_key = _rate_key_ip(ip)
    if ip_key and cache.get(ip_key, 0) >= OTP_MAX_PER_HOUR_PER_IP:
        raise ValueError("Too many requests. Try again later.")
    return _rate_key_phone(phone), ip_key


def _bump(phone_key, ip_key):
    for key in (phone_key, ip_key):
        if not key: continue
        try: cache.incr(key)
        except ValueError: cache.set(key, 1, timeout=3600)


@transaction.atomic
def issue_otp(phone, ip=None, purpose="login"):
    phone = (phone or "").strip()
    if not phone:
        raise ValueError("Phone is required.")
    phone_key, ip_key = _check_rate_limit(phone, ip)
    OTPCode.objects.filter(phone=phone, used_at__isnull=True).update(used_at=timezone.now())
    code = f"{secrets.randbelow(1_000_000):06d}"
    OTPCode.objects.create(phone=phone, code=code, purpose=purpose, ip_address=ip)
    _bump(phone_key, ip_key)
    return code


@transaction.atomic
def verify_otp(phone, code, purpose="login"):
    phone = (phone or "").strip()
    code = (code or "").strip()
    otp = (OTPCode.objects.select_for_update()
           .filter(phone=phone, purpose=purpose)
           .order_by("-created_at").first())
    if not otp: return False, "no_code"
    if otp.used_at: return False, "already_used"
    if timezone.now() - otp.created_at > timedelta(seconds=OTP_TTL):
        return False, "expired"
    if otp.attempts >= OTP_MAX_ATTEMPTS: return False, "too_many_attempts"
    if not secrets.compare_digest(otp.code, code):
        otp.attempts += 1; otp.save(update_fields=["attempts"])
        return False, "wrong_code"
    otp.used_at = timezone.now(); otp.save(update_fields=["used_at"])
    return True, "ok"

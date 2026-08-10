from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AuditLog
from .services import AuditService
from .middleware import get_current_user, get_current_request


def _get_audit_context():
    return get_current_user(), get_current_request()


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if sender == AuditLog:
        return
    if sender.__module__.startswith(("django.contrib", "django.db")):
        return

    user, request = _get_audit_context()
    if user:
        if created:
            AuditService.log_create(user, instance, request=request)
        else:
            # For updates, you may want to capture old values.
            # Use a pre_save hook or a dedicated package like django-auditlog.
            pass


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if sender == AuditLog:
        return
    user, request = _get_audit_context()
    if user:
        AuditService.log_delete(user, instance, request=request)
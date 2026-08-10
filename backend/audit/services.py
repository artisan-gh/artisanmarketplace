import traceback
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog
from .choices import AuditAction, AuditSeverity, HttpMethod


class AuditService:
    """
    Centralised audit logging service.
    Use this in all views, signals, and custom actions.
    """

    @staticmethod
    def log(action, user, instance=None, module=None,
            old_values=None, new_values=None, request=None,
            description="", correlation_id=None,
            success=True, severity=None,
            response_status=None, duration_ms=None,
            exception=None, **kwargs):
        # Determine module
        if not module and instance:
            module = instance._meta.app_label
        elif not module:
            module = "system"

        # Determine severity
        if severity is None:
            severity_map = {
                AuditAction.CREATE: AuditSeverity.MEDIUM,
                AuditAction.UPDATE: AuditSeverity.MEDIUM,
                AuditAction.DELETE: AuditSeverity.HIGH,
                AuditAction.SOFT_DELETE: AuditSeverity.HIGH,
                AuditAction.RESTORE: AuditSeverity.MEDIUM,
                AuditAction.LOGIN: AuditSeverity.LOW,
                AuditAction.LOGOUT: AuditSeverity.LOW,
                AuditAction.VIEW: AuditSeverity.LOW,
                AuditAction.EXPORT: AuditSeverity.HIGH,
                AuditAction.IMPORT: AuditSeverity.HIGH,
                AuditAction.DOWNLOAD: AuditSeverity.MEDIUM,
                AuditAction.UPLOAD: AuditSeverity.MEDIUM,
                AuditAction.PRINT: AuditSeverity.LOW,
                AuditAction.LOCK: AuditSeverity.MEDIUM,
                AuditAction.UNLOCK: AuditSeverity.MEDIUM,
                AuditAction.ARCHIVE: AuditSeverity.MEDIUM,
                AuditAction.UNARCHIVE: AuditSeverity.MEDIUM,
                AuditAction.MERGE: AuditSeverity.HIGH,
                AuditAction.SPLIT: AuditSeverity.HIGH,
                AuditAction.VERIFY: AuditSeverity.MEDIUM,
                AuditAction.UNVERIFY: AuditSeverity.MEDIUM,
                AuditAction.ASSIGN: AuditSeverity.MEDIUM,
                AuditAction.REASSIGN: AuditSeverity.MEDIUM,
                AuditAction.ESCALATE: AuditSeverity.HIGH,
                AuditAction.APPROVE: AuditSeverity.MEDIUM,
                AuditAction.REJECT: AuditSeverity.MEDIUM,
                AuditAction.COMPLETE: AuditSeverity.MEDIUM,
            }
            severity = severity_map.get(action, AuditSeverity.LOW)

        # Extract request context
        ip = None
        request_id = ""
        path = ""
        method = ""
        user_agent = ""
        if request:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
            if forwarded:
                ip = forwarded.split(",")[0].strip()
            else:
                ip = request.META.get("REMOTE_ADDR")
            request_id = request.META.get("HTTP_X_REQUEST_ID", "")
            path = request.path
            method = request.method or ""
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            if not correlation_id:
                correlation_id = request.META.get("HTTP_X_CORRELATION_ID", "")

        # Parse user agent
        browser = os = device = ""
        if user_agent:
            try:
                from user_agents import parse
                ua = parse(user_agent)
                browser = ua.browser.family if ua.browser else ""
                os = ua.os.family if ua.os else ""
                device = ua.device.family if ua.device else ""
            except ImportError:
                pass

        # Filter sensitive fields
        sensitive_keys = {"password", "token", "refresh_token", "access_token", "secret", "otp"}
        if old_values and isinstance(old_values, dict):
            old_values = {k: v for k, v in old_values.items() if k.lower() not in sensitive_keys}
        if new_values and isinstance(new_values, dict):
            new_values = {k: v for k, v in new_values.items() if k.lower() not in sensitive_keys}

        # Capture exception traceback
        exception_text = ""
        if exception:
            if isinstance(exception, Exception):
                exception_text = "".join(traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                ))
            else:
                exception_text = str(exception)

        # Determine content type and object id
        content_type = None
        object_id = ""
        object_repr = ""
        if instance:
            object_repr = str(instance)
            try:
                content_type = ContentType.objects.get_for_model(instance)
                object_id = str(instance.pk)
            except Exception:
                content_type = None
                object_id = ""

        return AuditLog.objects.create(
            user=user,
            action=action,
            module=module,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            old_values=old_values,
            new_values=new_values,
            success=success,
            response_status=response_status,
            duration_ms=duration_ms,
            request_id=request_id,
            correlation_id=correlation_id,
            ip_address=ip,
            path=path,
            method=method,
            user_agent=user_agent,
            browser=browser,
            operating_system=os,
            device=device,
            description=description,
            exception=exception_text,
            severity=severity,
            organization=getattr(user, "organization", None),
            **kwargs
        )

    # ─── Convenience methods ──────────────────────────────────

    @staticmethod
    def log_create(user, instance, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.CREATE,
            user=user,
            instance=instance,
            new_values=instance.__dict__,
            request=request,
            **kwargs
        )

    @staticmethod
    def log_update(user, instance, old_values, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.UPDATE,
            user=user,
            instance=instance,
            old_values=old_values,
            new_values=instance.__dict__,
            request=request,
            **kwargs
        )

    @staticmethod
    def log_delete(user, instance, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.DELETE,
            user=user,
            instance=instance,
            old_values=instance.__dict__,
            request=request,
            **kwargs
        )

    @staticmethod
    def log_soft_delete(user, instance, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.SOFT_DELETE,
            user=user,
            instance=instance,
            old_values=instance.__dict__,
            request=request,
            **kwargs
        )

    @staticmethod
    def log_restore(user, instance, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.RESTORE,
            user=user,
            instance=instance,
            new_values=instance.__dict__,
            request=request,
            **kwargs
        )

    @staticmethod
    def log_login(user, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.LOGIN,
            user=user,
            module="accounts",
            success=True,
            severity=AuditSeverity.LOW,
            request=request,
            **kwargs
        )

    @staticmethod
    def log_logout(user, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.LOGOUT,
            user=user,
            module="accounts",
            success=True,
            severity=AuditSeverity.LOW,
            request=request,
            **kwargs
        )

    @staticmethod
    def log_assign(user, instance, assigned_to, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.ASSIGN,
            user=user,
            instance=instance,
            new_values={"assigned_to": str(assigned_to)},
            request=request,
            description=f"Assigned to {assigned_to.get_full_name()}",
            **kwargs
        )

    @staticmethod
    def log_reassign(user, instance, assigned_to, old_artisan, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.REASSIGN,
            user=user,
            instance=instance,
            old_values={"assigned_to": str(old_artisan)},
            new_values={"assigned_to": str(assigned_to)},
            request=request,
            description=f"Reassigned from {old_artisan.get_full_name()} to {assigned_to.get_full_name()}",
            **kwargs
        )

    @staticmethod
    def log_escalate(user, instance, escalated_to, reason, request=None, **kwargs):
        return AuditService.log(
            action=AuditAction.ESCALATE,
            user=user,
            instance=instance,
            new_values={"escalated_to": str(escalated_to)},
            request=request,
            severity=AuditSeverity.HIGH,
            description=f"Escalated to {escalated_to.get_full_name()} because: {reason}",
            **kwargs
        )

    @staticmethod
    def log_exception(user, action, instance=None, request=None, exception=None, **kwargs):
        return AuditService.log(
            action=action,
            user=user,
            instance=instance,
            success=False,
            request=request,
            exception=exception,
            severity=AuditSeverity.HIGH,
            **kwargs
        )
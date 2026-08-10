from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AuditLog


@shared_task
def archive_old_audit_logs(days=365):
    """
    Archive audit logs older than `days` days.
    You can implement archival logic (move to separate table, mark as archived, etc.)
    """
    cutoff = timezone.now() - timedelta(days=days)
    count = AuditLog.objects.filter(created_at__lt=cutoff, archived=False).update(archived=True)
    return f"Archived {count} audit logs older than {days} days."
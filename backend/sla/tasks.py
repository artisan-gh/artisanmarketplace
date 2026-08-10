# sla/tasks.py
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import SLATracker
from incidents.models import Incident
from notifications.tasks import send_notification_task
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def check_and_escalate_slas():
    """
    Run periodically (e.g., every minute) to:
    1. Find SLAs that have passed their target resolution.
    2. Mark them as BREACHED.
    3. Escalate the incident (increase priority or reassign).
    4. Send notifications to the assigned artisan, supervisor, and manager.
    """
    now = timezone.now()

    # Find trackers that are overdue and not yet marked as breached
    breached = SLATracker.objects.filter(
        target_resolution__lt=now,
        sla_status__in=['ON_TRACK', 'AT_RISK']
    ).select_related('incident', 'incident__assigned_to', 'incident__supervisor')

    processed_count = 0

    for tracker in breached:
        incident = tracker.incident

        # 1. Update tracker status
        tracker.sla_status = 'BREACHED'
        tracker.save(update_fields=['sla_status'])

        # 2. Escalate the incident (increase priority)
        if incident.priority == 'LOW':
            incident.priority = 'MEDIUM'
        elif incident.priority == 'MEDIUM':
            incident.priority = 'HIGH'
        elif incident.priority == 'HIGH':
            incident.priority = 'CRITICAL'
        incident.save(update_fields=['priority'])

        # 3. Build recipient list (User objects)
        recipients = []

        # Notify the assigned artisan (if any)
        if incident.assigned_to:
            recipients.append(incident.assigned_to)

        # Notify the supervisor (if any)
        if incident.supervisor:
            recipients.append(incident.supervisor)

        # Optional: notify all managers/admins
        # managers = User.objects.filter(user_type='MANAGER', is_active=True)
        # recipients.extend(managers)

        # Remove duplicates
        unique_users = list(set(recipients))

        # Send notifications asynchronously
        for user in unique_users:
            send_notification_task.delay(
                user_id=user.id,
                subject=f'SLA Breached: {incident.incident_number}',
                message=(
                    f'Incident {incident.incident_number} has breached its SLA.\n'
                    f'Priority has been escalated to {incident.priority}.\n'
                    f'Customer: {incident.customer.name}\n'
                    f'Target Resolution: {tracker.target_resolution}\n'
                    f'Please take immediate action.'
                ),
                channel='email',  # or 'sms'
                notification_type='SLA',
                related_data={
                    'incident_id': str(incident.id),
                    'sla_tracker_id': str(tracker.id),
                }
            )

        processed_count += 1

    return f'Processed {processed_count} breached SLAs.'
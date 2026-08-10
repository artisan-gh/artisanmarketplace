# sla/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SLATracker
from notifications.tasks import send_notification_task

@receiver(post_save, sender=SLATracker)
def check_sla_status(sender, instance, created, **kwargs):
    incident = instance.incident

    if instance.sla_status == 'AT_RISK':
        assigned_user = incident.assigned_to
        if assigned_user:
            send_notification_task.delay(
                user_id=assigned_user.id,
                subject=f"SLA At Risk: {incident.incident_number}",
                message=f"Incident {incident.incident_number} is at risk of breaching SLA. Target: {instance.target_resolution}",
                channel='email',
                notification_type='SLA',
                related_data={'incident_id': str(incident.id)}
            )

    elif instance.sla_status == 'BREACHED':
        recipients = [incident.assigned_to, incident.supervisor]
        for user in recipients:
            if user:
                send_notification_task.delay(
                    user_id=user.id,
                    subject=f"SLA Breached: {incident.incident_number}",
                    message=f"Incident {incident.incident_number} has breached SLA. Action required.",
                    channel='email',
                    notification_type='SLA',
                    related_data={'incident_id': str(incident.id)}
                )
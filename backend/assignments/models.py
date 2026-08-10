from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Assignment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.OneToOneField('incidents.Incident', on_delete=models.CASCADE, related_name='assignment')
    artisan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type': 'ARTISAN'})
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assignments_made')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)

    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['artisan', 'status']),
            models.Index(fields=['incident']),
        ]

    def __str__(self):
        return f"{self.incident.incident_number} → {self.artisan.email}"

    def accept(self):
        self.status = 'ACCEPTED'
        self.accepted_at = timezone.now()
        self.save()

    def reject(self):
        self.status = 'REJECTED'
        self.save()

    def start(self):
        self.status = 'IN_PROGRESS'
        self.started_at = timezone.now()
        self.save()

    def complete(self):
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()

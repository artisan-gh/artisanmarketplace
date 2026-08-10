from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Incident(models.Model):
    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident_number = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='incidents')
    category = models.ForeignKey('incident_category.IncidentCategory', on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(   # ✅ Added
        'incident_category.SubCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents'
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.ForeignKey('incident_statuses.IncidentStatus', on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    resolution_notes = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_incidents')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='supervised_incidents')

    target_resolution = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['incident_number']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.incident_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.incident_number:
            last = Incident.objects.order_by('created_at').last()
            if last and last.incident_number:
                try:
                    num = int(last.incident_number.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            self.incident_number = f"INC-{num:06d}"
        super().save(*args, **kwargs)

from django.db import models
import uuid

class IncidentStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated code like STS-001")
    name = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    ordering = models.PositiveSmallIntegerField(default=0)
    color_code = models.CharField(max_length=7, blank=True, help_text="Hex color for UI")
    is_terminal = models.BooleanField(default=False, help_text="Is this a final status? (e.g., Resolved, Closed)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = "Incident Status"
        verbose_name_plural = "Incident Statuses"

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = IncidentStatus.objects.order_by('created_at').last()
            if last and last.code:
                try:
                    num = int(last.code.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            self.code = f"STS-{num:04d}"
        super().save(*args, **kwargs)

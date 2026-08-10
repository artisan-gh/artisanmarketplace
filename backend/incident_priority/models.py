from django.db import models
import uuid

class IncidentPriority(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated code like PRI-001")
    name = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    ordering = models.PositiveSmallIntegerField(default=0)
    resolution_hours = models.PositiveIntegerField(null=True, blank=True)
    escalation_hours = models.PositiveIntegerField(null=True, blank=True)
    color_code = models.CharField(max_length=7, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = "Incident Priority"
        verbose_name_plural = "Incident Priorities"

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = IncidentPriority.objects.order_by('created_at').last()
            if last and last.code:
                try:
                    num = int(last.code.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            self.code = f"PRI-{num:04d}"
        super().save(*args, **kwargs)

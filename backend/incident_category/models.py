from django.db import models
import uuid

class IncidentCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated code like CAT-001")
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    ordering = models.PositiveSmallIntegerField(default=0, help_text="Order in dropdowns")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = "Incident Category"
        verbose_name_plural = "Incident Categories"

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = IncidentCategory.objects.order_by('created_at').last()
            if last and last.code:
                try:
                    num = int(last.code.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            self.code = f"CAT-{num:04d}"
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated code like SUB-001")
    category = models.ForeignKey(
        IncidentCategory,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    ordering = models.PositiveSmallIntegerField(default=0, help_text="Order within category")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordering', 'name']
        unique_together = [['category', 'name']]
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = SubCategory.objects.order_by('created_at').last()
            if last and last.code:
                try:
                    num = int(last.code.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            self.code = f"SUB-{num:04d}"
        super().save(*args, **kwargs)

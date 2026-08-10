# artisan/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

# ─── Import incident category models ──────────────────────
from incident_category.models import IncidentCategory, SubCategory


class Skill(models.Model):
    """
    Legacy skill model – kept for backward compatibility.
    New skills should be stored as SubCategory references via ArtisanProfile.skills.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ArtisanProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='artisan_profile',
        limit_choices_to={'user_type': 'ARTISAN'}
    )

    # ─── New fields for category and skills (from incident_category) ──
    category = models.ForeignKey(
        IncidentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='artisans',
        help_text="Primary trade area (e.g., Construction, Electrical)"
    )
    skills = models.ManyToManyField(
        SubCategory,
        blank=True,
        related_name='artisans',
        help_text="Specific skills (subcategories) the artisan possesses"
    )

    # ─── Legacy skills (keep for existing data) ──────────────
    legacy_skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='artisans_legacy',
        help_text="Legacy skills (deprecated – use skills field instead)"
    )

    # ─── Availability & location ─────────────────────────────
    is_available = models.BooleanField(
        default=True,
        help_text="Whether the artisan is currently available for new jobs"
    )
    current_location_lat = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True
    )
    current_location_lng = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True
    )
    max_concurrent_jobs = models.PositiveSmallIntegerField(
        default=3,
        help_text="Maximum number of jobs the artisan can handle simultaneously"
    )
    average_rating = models.FloatField(
        default=0.0,
        help_text="Average rating from completed jobs (0-5)"
    )
    hire_date = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        verbose_name = "Artisan Profile"
        verbose_name_plural = "Artisan Profiles"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.email}"

    @property
    def current_workload(self):
        """Number of active jobs currently assigned."""
        return self.user.assigned_incidents.filter(
            assignment__status__in=['PENDING', 'ACCEPTED', 'IN_PROGRESS']
        ).count()

    @property
    def can_take_more(self):
        """Check if artisan can accept another job."""
        return self.current_workload < self.max_concurrent_jobs

    @property
    def skills_list(self):
        """Return a list of skill names (from SubCategory)."""
        return list(self.skills.values_list('name', flat=True))

    @property
    def category_name(self):
        """Return the category name."""
        return self.category.name if self.category else None


class ArtisanAvailability(models.Model):
    """
    Weekly availability schedule for an artisan.
    """
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    artisan = models.ForeignKey(
        ArtisanProfile,
        on_delete=models.CASCADE,
        related_name='availability'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working = models.BooleanField(
        default=True,
        help_text="Whether the artisan works on this day"
    )

    class Meta:
        unique_together = ['artisan', 'day_of_week']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.artisan.user.get_full_name()} - {self.get_day_of_week_display()}"
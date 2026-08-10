from django.db import models
from django.conf import settings
from django.utils.text import slugify
from common.models import TimeStampedModel
from companies.models import Company


class JobCategory(TimeStampedModel):
    """
    Category for job listings.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Job Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(TimeStampedModel):
    """
    A job listing posted by a company.
    """

    class JobType(models.TextChoices):
        FULL_TIME = 'FULL_TIME', 'Full Time'
        PART_TIME = 'PART_TIME', 'Part Time'
        CONTRACT = 'CONTRACT', 'Contract'
        FREELANCE = 'FREELANCE', 'Freelance'
        INTERNSHIP = 'INTERNSHIP', 'Internship'
        REMOTE = 'REMOTE', 'Remote'

    class ExperienceLevel(models.TextChoices):
        ENTRY = 'ENTRY', 'Entry Level'
        JUNIOR = 'JUNIOR', 'Junior'
        MID = 'MID', 'Mid-Level'
        SENIOR = 'SENIOR', 'Senior'
        LEAD = 'LEAD', 'Lead / Manager'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'
        FILLED = 'FILLED', 'Filled'

    # ─── Relations ────────────────────────────────────────────
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs'
    )

    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs'
    )

    # ─── Core ──────────────────────────────────────────────────
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, help_text="Job requirements and qualifications")
    responsibilities = models.TextField(blank=True, help_text="Key responsibilities")

    # ─── Classification ───────────────────────────────────────
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.MID)

    # ─── Location ─────────────────────────────────────────────
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # ─── Compensation ─────────────────────────────────────────
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='GHS')
    is_salary_negotiable = models.BooleanField(default=False)
    benefits = models.TextField(blank=True, help_text="List of benefits")

    # ─── Dates ─────────────────────────────────────────────────
    application_deadline = models.DateField(null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ─── Status ───────────────────────────────────────────────
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    # ─── Engagement ────────────────────────────────────────────
    views = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)

    # ─── Features ──────────────────────────────────────────────
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['category']),
            models.Index(fields=['job_type']),
            models.Index(fields=['location']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class JobApplication(TimeStampedModel):
    """
    A candidate's application for a job.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        REVIEWED = 'REVIEWED', 'Reviewed'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        INTERVIEW = 'INTERVIEW', 'Interview Scheduled'
        OFFERED = 'OFFERED', 'Offered'
        HIRED = 'HIRED', 'Hired'
        REJECTED = 'REJECTED', 'Rejected'

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )

    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes for employer")

    # Match score (if using AI matching)
    match_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ['job', 'candidate']

    def __str__(self):
        return f"{self.candidate.email} - {self.job.title}"


class SavedJob(TimeStampedModel):
    """
    A job saved/bookmarked by a user.
    """
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs'
    )

    class Meta:
        unique_together = ['job', 'user']

    def __str__(self):
        return f"{self.user.email} saved {self.job.title}"

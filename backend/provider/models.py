
from django.conf import settings
from django.db import models
from django.utils import timezone


class Assessment(models.Model):
    class Kind(models.TextChoices):
        PSYCHOMETRIC = "psychometric", "Psychometric"
        SKILL = "skill", "Skill"

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    questions = models.JSONField(default=list)
    duration_minutes = models.PositiveIntegerField(default=30)
    max_attempts = models.PositiveIntegerField(default=2)
    pass_threshold = models.PositiveSmallIntegerField(default=70)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.title} ({self.kind})"

    @property
    def questions_count(self):
        return len(self.questions or [])


class Skill(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    category_slug = models.CharField(max_length=80, blank=True)
    assessment = models.ForeignKey(
        Assessment, on_delete=models.PROTECT, related_name="skills",
        limit_choices_to={"kind": Assessment.Kind.SKILL},
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AssessmentAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="assessment_attempts",
    )
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="attempts",
    )
    attempt_number = models.PositiveSmallIntegerField()
    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    question_order = models.JSONField(default=list)
    answers = models.JSONField(default=dict)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    timed_out = models.BooleanField(default=False)
    breakdown = models.JSONField(default=list, blank=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-started_at"]
        unique_together = [("user", "assessment", "attempt_number")]
        indexes = [models.Index(fields=["user", "assessment", "-started_at"])]

    def __str__(self):
        return f"{self.user} · {self.assessment.slug} · attempt {self.attempt_number}"

    @property
    def duration_seconds(self):
        end = self.submitted_at or timezone.now()
        return max(0, int((end - self.started_at).total_seconds()))


class ArtisanSkill(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="artisan_skills",
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="artisans")
    passed_at = models.DateTimeField(default=timezone.now)
    best_score = models.FloatField(default=0.0)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="verified_artisan_skills",
    )
    is_revoked = models.BooleanField(default=False)

    class Meta:
        unique_together = [("user", "skill")]
        ordering = ["-passed_at"]

    def __str__(self):
        return f"{self.user} → {self.skill.name}"

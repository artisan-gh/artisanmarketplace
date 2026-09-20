"""
Ayuda Test Centre — installer for a Django + React monorepo.

Assumes:
    ./manage.py
    ./config/settings.py      (or ./settings.py, or ./core/settings.py)
    ./config/urls.py          (ROOT_URLCONF target)
    ./frontend/src/           (React app root; adjust REACT_SRC if different)

Writes:
    Django (backend):
        provider/__init__.py
        provider/apps.py
        provider/models.py
        provider/scoring.py
        provider/permissions.py
        provider/serializers.py
        provider/views.py
        provider/urls.py
        provider/admin.py
        provider/management/__init__.py
        provider/management/commands/__init__.py
        provider/management/commands/seed_test_centre.py

    React (frontend):
        frontend/src/components/provider/TestCentre.jsx
        frontend/src/components/provider/TestRunner.jsx
        frontend/src/components/provider/TestResult.jsx
        frontend/src/components/provider/TestCentre.css

Wires into existing files:
    INSTALLED_APPS     → adds "provider"
    ROOT_URLCONF       → adds include("provider.urls") under /api/provider/
    requirements.txt   → no new deps (uses existing Django REST Framework)

Safe to re-run: every step uses a marker or overwrites a file we own.
"""
from pathlib import Path
from datetime import datetime
import re
import shutil

ROOT = Path(".")
REACT_SRC = Path("../frontend/src")  # ← change if your React app is elsewhere


# ------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------
def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"  wrote   {path}")


def append_once(path, marker, content):
    p = ROOT / path
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    if marker in text:
        print(f"  skip    {path}")
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")
    print(f"  updated {path}")


def insert_before(path, needles, content):
    p = ROOT / path
    if not p.exists():
        print(f"  !!      {path} not found")
        return False
    text = p.read_text(encoding="utf-8")
    if content.strip() in text:
        print(f"  skip    {path}")
        return True
    for needle in (needles if isinstance(needles, list) else [needles]):
        if needle in text:
            p.write_text(text.replace(needle, content.strip() + "\n" + needle, 1), encoding="utf-8")
            print(f"  updated {path}")
            return True
    print(f"  !!      {path}: no marker found")
    return False


def replace_once(path, old, new, label="change"):
    p = ROOT / path
    if not p.exists():
        print(f"  !!      {path} not found")
        return False
    text = p.read_text(encoding="utf-8")
    if new.strip() in text:
        print(f"  skip    {path} ({label} already applied)")
        return True
    if old not in text:
        print(f"  !!      {path}: marker not found for {label}")
        return False
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"  updated {path} ({label})")
    return True


def backup(path):
    p = ROOT / path
    if not p.exists():
        return None
    name = f"{p.stem}.backup-{datetime.now():%Y%m%d-%H%M%S}{p.suffix}"
    shutil.copy2(p, p.parent / name)
    return name


def find_settings():
    for candidate in ("config/settings.py", "settings.py", "core/settings.py"):
        if (ROOT / candidate).exists():
            return candidate
    return None


def find_root_urls():
    settings = find_settings()
    if not settings:
        return None
    text = (ROOT / settings).read_text(encoding="utf-8")
    m = re.search(r'ROOT_URLCONF\s*=\s*[("\']([^"\']+)', text)
    if not m:
        return None
    return m.group(1).replace(".", "/") + ".py"


# ==================================================================
# START
# ==================================================================
print("\n=== Ayuda Test Centre installer (Django + React) ===\n")


# ------------------------------------------------------------------
# 1. Provider app skeleton
# ------------------------------------------------------------------
print("[1/15] provider package + apps.py")

write("provider/__init__.py", "")
write("provider/apps.py", r'''
from django.apps import AppConfig


class ProviderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "provider"
    verbose_name = "Provider (Ayuda Test Centre)"
''')
write("provider/management/__init__.py", "")
write("provider/management/commands/__init__.py", "")


# ------------------------------------------------------------------
# 2. models.py
# ------------------------------------------------------------------
print("\n[2/15] provider/models.py")

write("provider/models.py", r'''
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
''')


# ------------------------------------------------------------------
# 3. scoring.py
# ------------------------------------------------------------------
print("\n[3/15] provider/scoring.py")

write("provider/scoring.py", r'''
"""
Pure scoring functions. No DB, no request.

Question shape:
    {
        "id": "q1",
        "text": "...",
        "type": "single_choice" | "multiple_choice" | "boolean" | "likert" | "text",
        "options": [{"id": "a", "text": "..."}, ...],
        "correct": ["b"],        # ignored for psychometric
        "weight": 1,
        "trait": "conscientiousness"  # psychometric only
    }
"""
from typing import Any


def _normalize(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def _score_question(question: dict, answer: Any) -> tuple[float, bool, str]:
    qtype = question.get("type", "single_choice")
    weight = float(question.get("weight", 1))

    if qtype == "likert":
        try:
            n = int(answer)
        except (TypeError, ValueError):
            return 0.0, False, "invalid_likert_value"
        if not (1 <= n <= 5):
            return 0.0, False, "likert_out_of_range"
        return weight, True, "recorded"

    if qtype == "text":
        return 0.0, False, "text_not_scored"

    correct = set(_normalize(question.get("correct")))
    given = set(_normalize(answer))

    if not correct:
        return 0.0, False, "no_correct_configured"

    if qtype == "multiple_choice":
        return (weight, True, "correct") if given == correct else (0.0, False, "incorrect")

    return (weight, True, "correct") if (len(given) == 1 and given == correct) else (0.0, False, "incorrect")


def score_attempt(assessment, answers: dict) -> dict:
    questions = assessment.questions or []
    total_weight = earned_weight = 0.0
    breakdown = []
    trait_buckets: dict[str, list[float]] = {}

    for q in questions:
        qid = str(q.get("id"))
        qtype = q.get("type", "single_choice")
        weight = float(q.get("weight", 1))
        answer = answers.get(qid)
        awarded, correct, reason = _score_question(q, answer)

        if assessment.kind == "psychometric" and qtype == "likert":
            trait = q.get("trait") or "general"
            try:
                trait_buckets.setdefault(trait, []).append(float(answer))
            except (TypeError, ValueError):
                pass

        if qtype in ("single_choice", "multiple_choice", "boolean"):
            total_weight += weight
            earned_weight += awarded

        breakdown.append({
            "question_id": qid, "type": qtype, "correct": correct,
            "awarded": awarded, "reason": reason,
        })

    if assessment.kind == "psychometric":
        score, passed = _score_psychometric(assessment, trait_buckets)
    else:
        score = round((earned_weight / total_weight) * 100, 2) if total_weight else 0.0
        passed = score >= assessment.pass_threshold

    return {
        "score": score,
        "passed": passed,
        "breakdown": breakdown,
        "trait_scores": {k: round(sum(v) / len(v), 3) for k, v in trait_buckets.items() if v},
    }


def _score_psychometric(assessment, trait_buckets) -> tuple[float, bool]:
    if not trait_buckets:
        return 0.0, False
    avgs = {t: sum(v) / len(v) for t, v in trait_buckets.items() if v}
    if not avgs:
        return 0.0, False
    overall = sum(avgs.values()) / len(avgs)
    score = round((overall / 5.0) * 100, 2)
    passed = all(a >= 3.0 for a in avgs.values()) and score >= assessment.pass_threshold
    return score, passed
''')


# ------------------------------------------------------------------
# 4. permissions.py
# ------------------------------------------------------------------
print("\n[4/15] provider/permissions.py")

write("provider/permissions.py", r'''
from rest_framework import permissions


PROVIDER_USER_TYPES = {"ARTISAN", "PROVIDER", "AGENT"}


def _user_type(user) -> str:
    return (getattr(user, "user_type", "") or "").upper()


class IsProvider(permissions.BasePermission):
    message = "Only service providers can access the Test Centre."

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and _user_type(u) in PROVIDER_USER_TYPES)


class IsAttemptOwner(permissions.BasePermission):
    message = "You do not have access to this attempt."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsSupportStaff(permissions.BasePermission):
    message = "Only support staff can reset attempts."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
''')


# ------------------------------------------------------------------
# 5. serializers.py
# ------------------------------------------------------------------
print("\n[5/15] provider/serializers.py")

write("provider/serializers.py", r'''
from django.utils import timezone
from rest_framework import serializers

from .models import Assessment, AssessmentAttempt, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "slug", "name", "description", "category_slug"]


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.CharField()
    answer = serializers.JSONField(required=False, allow_null=True)


class SubmitAttemptSerializer(serializers.Serializer):
    answers = SubmitAnswerSerializer(many=True)

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("answers cannot be empty.")
        return value


def public_questions(assessment: Assessment) -> list[dict]:
    """Strip `correct` so it never leaves the server."""
    return [
        {
            "id": q.get("id"),
            "text": q.get("text"),
            "type": q.get("type", "single_choice"),
            "options": q.get("options", []),
            "weight": q.get("weight", 1),
        }
        for q in (assessment.questions or [])
    ]


def _psychometric_passed(user) -> bool:
    return AssessmentAttempt.objects.filter(
        user=user,
        assessment__kind=Assessment.Kind.PSYCHOMETRIC,
        is_submitted=True,
        passed=True,
    ).exists()


def compute_user_status(assessment: Assessment, user) -> dict:
    attempts = AssessmentAttempt.objects.filter(user=user, assessment=assessment)
    used = attempts.count()
    best = attempts.filter(is_submitted=True).order_by("-score").first()
    last = attempts.order_by("-started_at").first()
    active = attempts.filter(is_submitted=False, expires_at__gt=timezone.now()).first()
    passing = attempts.filter(is_submitted=True, passed=True).first()

    is_locked = False
    lock_reason = None
    if assessment.kind == Assessment.Kind.SKILL and not _psychometric_passed(user):
        is_locked = True
        lock_reason = "Pass the psychometric test to unlock skill tests."

    if passing:
        status = "PASSED"
    elif is_locked:
        status = "LOCKED"
    elif active:
        status = "IN_PROGRESS"
    elif used >= assessment.max_attempts:
        status = "EXHAUSTED"
    else:
        status = "READY"

    skill = assessment.skills.first() if assessment.kind == Assessment.Kind.SKILL else None

    return {
        "attempts_used": used,
        "best_score": best.score if best else None,
        "last_attempt_id": last.id if last else None,
        "status": status,
        "can_start": status in {"READY", "IN_PROGRESS"},
        "is_locked": is_locked,
        "lock_reason": lock_reason,
        "skill": skill,
        "active_attempt_id": active.id if active else None,
    }


def serialize_assessment(a: Assessment, meta: dict) -> dict:
    return {
        "id": a.id,
        "slug": a.slug,
        "title": a.title,
        "kind": a.kind,
        "description": a.description,
        "instructions": a.instructions,
        "duration_minutes": a.duration_minutes,
        "max_attempts": a.max_attempts,
        "pass_threshold": a.pass_threshold,
        "questions_count": a.questions_count,
        "status": meta["status"],
        "attempts_used": meta["attempts_used"],
        "best_score": meta["best_score"],
        "last_attempt_id": meta["last_attempt_id"],
        "active_attempt_id": meta["active_attempt_id"],
        "can_start": meta["can_start"],
        "is_locked": meta["is_locked"],
        "lock_reason": meta["lock_reason"],
        "skill": (
            {
                "id": meta["skill"].id,
                "slug": meta["skill"].slug,
                "name": meta["skill"].name,
                "description": meta["skill"].description,
                "category_slug": meta["skill"].category_slug,
            }
            if meta.get("skill") else None
        ),
    }
''')


# ------------------------------------------------------------------
# 6. views.py
# ------------------------------------------------------------------
print("\n[6/15] provider/views.py")

write("provider/views.py", r'''
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Assessment, AssessmentAttempt, ArtisanSkill
from .permissions import IsAttemptOwner, IsProvider, IsSupportStaff
from .scoring import score_attempt
from .serializers import (
    SubmitAttemptSerializer,
    compute_user_status,
    public_questions,
    serialize_assessment,
)


class AssessmentListView(APIView):
    permission_classes = [IsProvider]

    def get(self, request):
        qs = Assessment.objects.filter(is_active=True).prefetch_related("skills")
        data = [serialize_assessment(a, compute_user_status(a, request.user)) for a in qs]
        return Response({
            "psychometric": [r for r in data if r["kind"] == "psychometric"],
            "skill_tests": [r for r in data if r["kind"] == "skill"],
        })


class AssessmentDetailView(APIView):
    permission_classes = [IsProvider]

    def get(self, request, slug):
        a = get_object_or_404(Assessment, slug=slug, is_active=True)
        return Response(serialize_assessment(a, compute_user_status(a, request.user)))


class StartAttemptView(APIView):
    permission_classes = [IsProvider]

    @transaction.atomic
    def post(self, request, slug):
        assessment = get_object_or_404(Assessment, slug=slug, is_active=True)
        attempts = AssessmentAttempt.objects.select_for_update().filter(
            user=request.user, assessment=assessment,
        )

        if assessment.kind == Assessment.Kind.SKILL and not _psychometric_passed(request.user):
            return Response(
                {"detail": "Pass the psychometric test to unlock skill tests."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if attempts.filter(is_submitted=True, passed=True).exists():
            return Response(
                {"detail": "You have already passed this assessment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active = attempts.filter(is_submitted=False, expires_at__gt=timezone.now()).first()
        if active:
            return Response(_start_payload(active, assessment))

        used = attempts.count()
        if used >= assessment.max_attempts:
            return Response(
                {"detail": "No attempts remaining. Contact support to reset."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            assessment=assessment,
            attempt_number=used + 1,
            started_at=now,
            expires_at=now + timezone.timedelta(minutes=assessment.duration_minutes),
            question_order=[q.get("id") for q in assessment.questions or []],
        )
        return Response(_start_payload(attempt, assessment), status=status.HTTP_201_CREATED)


class SubmitAttemptView(APIView):
    permission_classes = [IsProvider, IsAttemptOwner]

    @transaction.atomic
    def post(self, request, pk):
        attempt = get_object_or_404(
            AssessmentAttempt.objects.select_for_update().select_related("assessment"),
            pk=pk, user=request.user,
        )
        if attempt.is_submitted:
            return Response(
                {"detail": "This attempt has already been submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubmitAttemptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = {a["question_id"]: a.get("answer") for a in serializer.validated_data["answers"]}
        now = timezone.now()

        result = score_attempt(attempt.assessment, answers)

        attempt.answers = answers
        attempt.score = result["score"]
        attempt.passed = result["passed"]
        attempt.breakdown = result["breakdown"]
        attempt.submitted_at = now
        attempt.timed_out = now > attempt.expires_at
        attempt.is_submitted = True
        attempt.save(update_fields=[
            "answers", "score", "passed", "breakdown",
            "submitted_at", "timed_out", "is_submitted",
        ])

        skill_unlocked = None
        if attempt.passed and attempt.assessment.kind == Assessment.Kind.SKILL:
            skill = attempt.assessment.skills.filter(is_active=True).first()
            if skill:
                prev = ArtisanSkill.objects.filter(user=request.user, skill=skill).first()
                best = max(result["score"], prev.best_score if prev else 0)
                obj, _ = ArtisanSkill.objects.update_or_create(
                    user=request.user, skill=skill,
                    defaults={"passed_at": now, "best_score": best},
                )
                skill_unlocked = obj.skill

        return Response(_result_payload(attempt, result, skill_unlocked))


class ResultView(APIView):
    permission_classes = [IsProvider, IsAttemptOwner]

    def get(self, request, pk):
        attempt = get_object_or_404(
            AssessmentAttempt.objects.select_related("assessment"),
            pk=pk, user=request.user,
        )
        if not attempt.is_submitted:
            return Response(
                {"detail": "Attempt is not yet submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        skill_unlocked = None
        if attempt.passed and attempt.assessment.kind == Assessment.Kind.SKILL:
            skill = attempt.assessment.skills.first()
            if skill and ArtisanSkill.objects.filter(user=request.user, skill=skill).exists():
                skill_unlocked = skill
        result = {
            "score": attempt.score or 0,
            "passed": attempt.passed,
            "breakdown": attempt.breakdown or [],
            "trait_scores": {},
        }
        return Response(_result_payload(attempt, result, skill_unlocked))


class ResetAttemptsView(APIView):
    permission_classes = [IsSupportStaff]

    @transaction.atomic
    def post(self, request, slug):
        assessment = get_object_or_404(Assessment, slug=slug)
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required."}, status=400)
        deleted, _ = AssessmentAttempt.objects.filter(
            user_id=user_id, assessment=assessment,
        ).delete()
        return Response({"deleted_attempts": deleted})


def _start_payload(attempt, assessment):
    return {
        "attempt_id": attempt.id,
        "assessment_slug": assessment.slug,
        "assessment_title": assessment.title,
        "kind": assessment.kind,
        "started_at": attempt.started_at,
        "expires_at": attempt.expires_at,
        "duration_minutes": assessment.duration_minutes,
        "attempt_number": attempt.attempt_number,
        "questions": public_questions(assessment),
    }


def _result_payload(attempt, result, skill_unlocked):
    return {
        "attempt_id": attempt.id,
        "assessment_slug": attempt.assessment.slug,
        "assessment_title": attempt.assessment.title,
        "kind": attempt.assessment.kind,
        "score": result.get("score", 0),
        "passed": result.get("passed", False),
        "pass_threshold": attempt.assessment.pass_threshold,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "duration_seconds": attempt.duration_seconds,
        "timed_out": attempt.timed_out,
        "breakdown": result.get("breakdown", []),
        "trait_scores": result.get("trait_scores", {}),
        "skill_unlocked": (
            {
                "id": skill_unlocked.id,
                "slug": skill_unlocked.slug,
                "name": skill_unlocked.name,
                "description": skill_unlocked.description,
                "category_slug": skill_unlocked.category_slug,
            }
            if skill_unlocked else None
        ),
    }


def _psychometric_passed(user) -> bool:
    return AssessmentAttempt.objects.filter(
        user=user,
        assessment__kind=Assessment.Kind.PSYCHOMETRIC,
        is_submitted=True,
        passed=True,
    ).exists()
''')


# ------------------------------------------------------------------
# 7. urls.py
# ------------------------------------------------------------------
print("\n[7/15] provider/urls.py")

write("provider/urls.py", r'''
from django.urls import path

from .views import (
    AssessmentDetailView,
    AssessmentListView,
    ResetAttemptsView,
    ResultView,
    StartAttemptView,
    SubmitAttemptView,
)

app_name = "provider"

urlpatterns = [
    path("assessments/", AssessmentListView.as_view(), name="assessment-list"),
    path("assessments/<slug:slug>/", AssessmentDetailView.as_view(), name="assessment-detail"),
    path("assessments/<slug:slug>/start/", StartAttemptView.as_view(), name="assessment-start"),
    path("attempts/<int:pk>/submit/", SubmitAttemptView.as_view(), name="attempt-submit"),
    path("attempts/<int:pk>/result/", ResultView.as_view(), name="attempt-result"),
    path("assessments/<slug:slug>/reset/", ResetAttemptsView.as_view(), name="assessment-reset"),
]
''')


# ------------------------------------------------------------------
# 8. admin.py
# ------------------------------------------------------------------
print("\n[8/15] provider/admin.py")

write("provider/admin.py", r'''
from django.contrib import admin

from .models import ArtisanSkill, Assessment, AssessmentAttempt, Skill


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "kind", "duration_minutes",
                    "max_attempts", "pass_threshold", "is_active", "order")
    list_filter = ("kind", "is_active")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "assessment", "category_slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "assessment", "attempt_number", "score",
                    "passed", "timed_out", "started_at", "submitted_at")
    list_filter = ("passed", "timed_out", "assessment__kind", "assessment")
    search_fields = ("user__username", "user__email", "assessment__slug")
    date_hierarchy = "started_at"
    readonly_fields = ("started_at", "expires_at", "submitted_at", "answers",
                       "breakdown", "question_order")


@admin.register(ArtisanSkill)
class ArtisanSkillAdmin(admin.ModelAdmin):
    list_display = ("user", "skill", "passed_at", "best_score", "is_revoked")
    list_filter = ("is_revoked", "skill")
    search_fields = ("user__username", "user__email", "skill__name")
    date_hierarchy = "passed_at"
''')


# ------------------------------------------------------------------
# 9. seed command
# ------------------------------------------------------------------
print("\n[9/15] provider/management/commands/seed_test_centre.py")

write("provider/management/commands/seed_test_centre.py", r'''
from django.core.management.base import BaseCommand

from provider.models import Assessment, Skill


PSYCHOMETRIC_QUESTIONS = [
    {"id": f"p{i}", "text": f"Sample psychometric prompt {i}",
     "type": "likert",
     "trait": "conscientiousness" if i % 2 == 0 else "openness",
     "weight": 1}
    for i in range(1, 16)
]

ELECTRICAL_QUESTIONS = [
    {"id": f"e{i}", "text": f"Sample electrical question {i}",
     "type": "single_choice",
     "options": [
         {"id": "a", "text": "Option A"},
         {"id": "b", "text": "Option B"},
         {"id": "c", "text": "Option C"},
         {"id": "d", "text": "Option D"},
     ],
     "correct": ["b"], "weight": 1}
    for i in range(1, 16)
]

PLUMBING_QUESTIONS = [
    {"id": f"pl{i}", "text": f"Sample plumbing question {i}",
     "type": "single_choice",
     "options": [
         {"id": "a", "text": "Option A"},
         {"id": "b", "text": "Option B"},
         {"id": "c", "text": "Option C"},
         {"id": "d", "text": "Option D"},
     ],
     "correct": ["a"], "weight": 1}
    for i in range(1, 16)
]


class Command(BaseCommand):
    help = "Seed the Test Centre with a psychometric test and skill tests."

    def handle(self, *args, **options):
        psych, _ = Assessment.objects.update_or_create(
            slug="psychometric",
            defaults={
                "title": "Psychometric Test",
                "kind": Assessment.Kind.PSYCHOMETRIC,
                "description": (
                    "Psychometric Test is an assessment conducted to objectively "
                    "measure an individual's personality, aptitude, intelligence, "
                    "abilities and behavioral traits."
                ),
                "duration_minutes": 30, "max_attempts": 2,
                "pass_threshold": 60,
                "questions": PSYCHOMETRIC_QUESTIONS, "order": 0,
            },
        )

        electrical, _ = Assessment.objects.update_or_create(
            slug="electrical-services",
            defaults={
                "title": "Electrical Services Skill Test",
                "kind": Assessment.Kind.SKILL,
                "description": "Technical assessment for Electrical Services proficiency.",
                "duration_minutes": 30, "max_attempts": 2,
                "pass_threshold": 70,
                "questions": ELECTRICAL_QUESTIONS, "order": 1,
            },
        )

        plumbing, _ = Assessment.objects.update_or_create(
            slug="plumbing-services",
            defaults={
                "title": "Plumbing Services Skill Test",
                "kind": Assessment.Kind.SKILL,
                "description": "Technical assessment for Plumbing Services proficiency.",
                "duration_minutes": 30, "max_attempts": 2,
                "pass_threshold": 70,
                "questions": PLUMBING_QUESTIONS, "order": 2,
            },
        )

        Skill.objects.update_or_create(
            slug="electrical-services",
            defaults={
                "name": "Electrical Services",
                "description": "Electrical installation, wiring, and repairs.",
                "category_slug": "electrical",
                "assessment": electrical,
            },
        )
        Skill.objects.update_or_create(
            slug="plumbing-services",
            defaults={
                "name": "Plumbing Services",
                "description": "Pipe fitting, leak repairs, and drainage.",
                "category_slug": "plumbing",
                "assessment": plumbing,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"Test Centre seeded — psychometric #{psych.id}, "
            f"{Assessment.objects.filter(kind='skill').count()} skill tests."
        ))
''')


# ------------------------------------------------------------------
# 10. React — TestCentre.jsx
# ------------------------------------------------------------------
print("\n[10/15] React — TestCentre.jsx")

write(f"{REACT_SRC}/components/provider/TestCentre.jsx", r'''
// src/components/provider/TestCentre.jsx
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  FaThLarge, FaRegEdit, FaRegClipboard, FaBookOpen, FaLock,
  FaChevronRight, FaCheckCircle, FaBrain, FaBolt, FaClock,
  FaListOl, FaRedo, FaHeadset, FaCircleNotch, FaSignOutAlt,
} from 'react-icons/fa';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import './TestCentre.css';

const NAV_ITEMS = [
  { to: '/artisan/dashboard', label: 'Dashboard', icon: FaThLarge, end: true },
  { to: '/artisan/profile', label: 'My details', icon: FaRegEdit },
  { to: '/provider/test-centre', label: 'Test centre', icon: FaRegClipboard },
  { to: '/provider/training-centre', label: 'Training centre', icon: FaBookOpen, locked: true },
];

const containerVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } },
};
const itemVariants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
};

const STATUS_LABEL = {
  PASSED: 'PASSED',
  READY: 'READY',
  LOCKED: 'LOCKED',
  IN_PROGRESS: 'IN PROGRESS',
  EXHAUSTED: 'NO ATTEMPTS',
};

const statusTone = (s) => {
  if (s === 'PASSED') return 'success';
  if (s === 'READY' || s === 'IN_PROGRESS') return 'ready';
  return 'locked';
};

const AssessmentCard = ({ assessment, onStart }) => {
  const tone = statusTone(assessment.status);
  const actionLabel =
    assessment.status === 'PASSED' ? 'VIEW RESULT'
    : assessment.status === 'IN_PROGRESS' ? 'RESUME'
    : assessment.status === 'LOCKED' ? 'LOCKED'
    : assessment.status === 'EXHAUSTED' ? 'CONTACT SUPPORT'
    : 'START';

  return (
    <motion.article className="tc-card" variants={itemVariants}>
      <div className="tc-card__head">
        <h3 className="tc-card__title">{assessment.title}</h3>
        <span className={`tc-status tc-status--${tone}`}>
          {STATUS_LABEL[assessment.status] || assessment.status}
        </span>
      </div>

      <p className="tc-card__desc">{assessment.description}</p>

      <div className="tc-card__meta">
        <div className="tc-meta">
          <span className="tc-meta__label"><FaListOl /> Questions</span>
          <span className="tc-meta__value">{assessment.questions_count}</span>
        </div>
        <div className="tc-meta">
          <span className="tc-meta__label"><FaClock /> Time</span>
          <span className="tc-meta__value">{assessment.duration_minutes} min</span>
        </div>
        <div className="tc-meta">
          <span className="tc-meta__label"><FaRedo /> Attempts</span>
          <span className="tc-meta__value">
            {assessment.attempts_used} / {assessment.max_attempts}
          </span>
        </div>
      </div>

      <button
        type="button"
        className={`tc-cta tc-cta--${tone}`}
        onClick={() => onStart(assessment)}
        disabled={!assessment.can_start && assessment.status !== 'IN_PROGRESS' && assessment.status !== 'PASSED'}
      >
        {actionLabel}
      </button>
    </motion.article>
  );
};

export const TestCentre = () => {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const fullName = user?.full_name || user?.name || 'Artisan';
  const firstName = fullName.split(' ')[0] || 'Artisan';
  const avatarUrl = user?.profile_picture || null;

  const { data, isLoading, error } = useQuery({
    queryKey: ['testCentre'],
    queryFn: () => api.get('/provider/assessments/').then((r) => r.data),
  });

  const handleStart = async (assessment) => {
    if (assessment.status === 'PASSED' && assessment.last_attempt_id) {
      navigate(`/provider/test-centre/result/${assessment.last_attempt_id}`);
      return;
    }
    if (assessment.status === 'IN_PROGRESS' && assessment.active_attempt_id) {
      navigate(`/provider/test-centre/${assessment.slug}/run`);
      return;
    }
    try {
      await api.post(`/provider/assessments/${assessment.slug}/start/`);
      navigate(`/provider/test-centre/${assessment.slug}/run`);
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Could not start the test.';
      window.alert(msg);
    }
  };

  const psychometric = data?.psychometric || [];
  const skillTests = data?.skill_tests || [];
  const anySkillLocked = skillTests.some((s) => s.is_locked);

  return (
    <div className="tc-layout">
      <aside className="ay-sidebar">
        <div className="ay-sidebar__brand">
          <div className="ay-sidebar__logo">
            <span className="ay-sidebar__logo-mark" />
            <span className="ay-sidebar__logo-text">yuda</span>
          </div>
          <p className="ay-sidebar__brand-sub">…here to help</p>
          <p className="ay-sidebar__brand-title">Service provider portal</p>
        </div>

        <nav className="ay-nav" aria-label="Primary">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end, locked }) => (
            <Link
              key={to}
              to={locked ? '#' : to}
              end={end}
              className={({ isActive }) =>
                `ay-nav__item ${isActive && !locked ? 'is-active' : ''} ${locked ? 'is-locked' : ''}`
              }
              onClick={(e) => locked && e.preventDefault()}
            >
              <span className="ay-nav__icon"><Icon /></span>
              <span className="ay-nav__label">{label}</span>
              {locked && <FaLock className="ay-nav__lock" />}
            </Link>
          ))}
        </nav>

        <div className="ay-sidebar__footer">
          <div className="ay-sidebar__avatar">
            {avatarUrl ? <img src={avatarUrl} alt={fullName} /> : <span>{firstName.charAt(0).toUpperCase()}</span>}
            <span className="ay-sidebar__avatar-dot" />
          </div>
          <div className="ay-sidebar__profile">
            <strong>{fullName}</strong>
            <span>Artisan</span>
          </div>
          <button type="button" onClick={logout} className="ay-sidebar__chev" aria-label="Sign out">
            <FaSignOutAlt />
          </button>
        </div>
      </aside>

      <main className="tc-main">
        <motion.div className="tc-inner" variants={containerVariants} initial="hidden" animate="show">
          <motion.header className="tc-hero" variants={itemVariants}>
            <div className="tc-hero__icon"><FaBrain /></div>
            <h1>Ayuda Test Centre</h1>
            <p>
              Prove your proficiency in your chosen fields. Complete psychometric
              and skill tests and get assigned high profile jobs.
            </p>
          </motion.header>

          <motion.section className="tc-section" variants={itemVariants}>
            <div className="tc-section__head">
              <span className="tc-section__icon"><FaRegClipboard /></span>
              <h2>Mandatory Assessments</h2>
            </div>

            {isLoading ? (
              <div className="tc-loading">
                <FaCircleNotch className="tc-spin" /> Loading…
              </div>
            ) : error ? (
              <div className="tc-error">Failed to load assessments.</div>
            ) : psychometric.length === 0 ? (
              <div className="tc-empty">No mandatory assessments yet.</div>
            ) : (
              <div className="tc-skill-grid">
                {psychometric.map((a) => (
                  <AssessmentCard key={a.id} assessment={a} onStart={handleStart} />
                ))}
              </div>
            )}
          </motion.section>

          <motion.section className="tc-section" variants={itemVariants}>
            <div className="tc-section__head">
              <span className="tc-section__icon tc-section__icon--bolt"><FaBolt /></span>
              <div>
                <h2>Skill Tests</h2>
                {anySkillLocked && (
                  <p className="tc-section__sub">
                    Pass the psychometric test to unlock skill tests. You will not
                    be assigned jobs with skills you haven&apos;t passed.
                  </p>
                )}
              </div>
            </div>

            {isLoading ? null : anySkillLocked ? (
              <div className="tc-locked">
                <span className="tc-locked__icon"><FaLock /></span>
                <div>
                  <strong>Pass the psychometric test to unlock skill tests</strong>
                  <p>You will not be assigned jobs with skills you haven&apos;t passed.</p>
                </div>
              </div>
            ) : skillTests.length === 0 ? (
              <div className="tc-empty">No skill tests available yet.</div>
            ) : (
              <div className="tc-skill-grid">
                {skillTests.map((a) => (
                  <AssessmentCard key={a.id} assessment={a} onStart={handleStart} />
                ))}
              </div>
            )}
          </motion.section>

          <motion.section className="tc-help" variants={itemVariants}>
            <div className="tc-help__left">
              <span className="tc-help__icon"><FaHeadset /></span>
              <div>
                <strong>Help Center</strong>
                <p>
                  Need assistance or reached your maximum attempts? Contact
                  support for a reset and get back on track.
                </p>
              </div>
            </div>
            <a href="mailto:support@ayuda.app" className="tc-help__btn">
              Contact Support
            </a>
          </motion.section>
        </motion.div>
      </main>
    </div>
  );
};

export default TestCentre;
''')


# ------------------------------------------------------------------
# 11. React — TestRunner.jsx
# ------------------------------------------------------------------
print("\n[11/15] React — TestRunner.jsx")

write(f"{REACT_SRC}/components/provider/TestRunner.jsx", r'''
// src/components/provider/TestRunner.jsx
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { FaClock, FaCircleNotch, FaCheckCircle } from 'react-icons/fa';
import api from '../../api/client';
import './TestCentre.css';

const AUTOSAVE_KEY = (slug) => `ayuda.testcentre.draft.${slug}`;

export const TestRunner = () => {
  const { slug } = useParams();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState(null);
  const [answers, setAnswers] = useState({});
  const [index, setIndex] = useState(0);
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [confirming, setConfirming] = useState(false);
  const tickRef = useRef(null);

  // Start (or resume) an attempt on mount
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const { data } = await api.post(`/provider/assessments/${slug}/start/`);
        if (cancelled) return;
        setAttempt(data);

        const cached = localStorage.getItem(AUTOSAVE_KEY(slug));
        if (cached) {
          try { setAnswers(JSON.parse(cached)); } catch {}
        }

        const expires = new Date(data.expires_at).getTime();
        const tick = () => {
          const left = Math.max(0, Math.floor((expires - Date.now()) / 1000));
          setSecondsLeft(left);
          if (left <= 0) {
            clearInterval(tickRef.current);
            submit(true);
          }
        };
        tick();
        tickRef.current = setInterval(tick, 1000);
      } catch (err) {
        if (!cancelled) {
          setError(err?.response?.data?.detail || 'Could not start the test.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
      if (tickRef.current) clearInterval(tickRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  const questions = attempt?.questions || [];
  const question = questions[index];
  const total = questions.length;

  // Autosave
  useEffect(() => {
    if (!slug) return;
    try { localStorage.setItem(AUTOSAVE_KEY(slug), JSON.stringify(answers)); } catch {}
  }, [answers, slug]);

  const progressPct = useMemo(
    () => (total ? ((index + 1) / total) * 100 : 0),
    [index, total]
  );

  const setAnswer = (qid, value) => {
    setAnswers((prev) => ({ ...prev, [qid]: value }));
  };

  const toggleMulti = (qid, optionId) => {
    setAnswers((prev) => {
      const current = Array.isArray(prev[qid]) ? prev[qid] : [];
      return {
        ...prev,
        [qid]: current.includes(optionId)
          ? current.filter((x) => x !== optionId)
          : [...current, optionId],
      };
    });
  };

  const submit = async (auto = false) => {
    if (!attempt) return;
    if (!auto && !window.confirm('Submit your answers now?')) return;
    try {
      const payload = {
        answers: Object.entries(answers).map(([question_id, answer]) => ({
          question_id, answer,
        })),
      };
      const { data } = await api.post(`/provider/attempts/${attempt.attempt_id}/submit/`, payload);
      localStorage.removeItem(AUTOSAVE_KEY(slug));
      navigate(`/provider/test-centre/result/${data.attempt_id}`);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not submit the test.');
    }
  };

  const renderInput = () => {
    if (!question) return null;
    const value = answers[question.id];

    if (question.type === 'likert') {
      return (
        <div className="tr-likert">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              className={`tr-likert__opt ${value === n ? 'is-selected' : ''}`}
              onClick={() => setAnswer(question.id, n)}
            >
              {n}
            </button>
          ))}
        </div>
      );
    }

    if (question.type === 'boolean') {
      return (
        <div className="tr-options">
          {['true', 'false'].map((opt) => (
            <button
              key={opt}
              type="button"
              className={`tr-option ${String(value) === opt ? 'is-selected' : ''}`}
              onClick={() => setAnswer(question.id, opt === 'true')}
            >
              {opt === 'true' ? 'True' : 'False'}
            </button>
          ))}
        </div>
      );
    }

    if (question.type === 'multiple_choice') {
      const current = Array.isArray(value) ? value : [];
      return (
        <div className="tr-options">
          {question.options.map((opt) => (
            <button
              key={opt.id}
              type="button"
              className={`tr-option ${current.includes(opt.id) ? 'is-selected' : ''}`}
              onClick={() => toggleMulti(question.id, opt.id)}
            >
              {opt.text}
            </button>
          ))}
        </div>
      );
    }

    // single_choice default
    return (
      <div className="tr-options">
        {question.options.map((opt) => (
          <button
            key={opt.id}
            type="button"
            className={`tr-option ${value === opt.id ? 'is-selected' : ''}`}
            onClick={() => setAnswer(question.id, opt.id)}
          >
            {opt.text}
          </button>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="tr-page">
        <div className="tc-loading"><FaCircleNotch className="tc-spin" /> Preparing your test…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="tr-page">
        <div className="tc-error">{error}</div>
      </div>
    );
  }

  const mm = String(Math.floor(secondsLeft / 60)).padStart(2, '0');
  const ss = String(secondsLeft % 60).padStart(2, '0');
  const timerTone = secondsLeft <= 60 ? 'danger' : secondsLeft <= 300 ? 'warning' : '';

  return (
    <div className="tr-page">
      <header className="tr-header">
        <div className="tr-header__left">
          <span className="tr-dot" />
          <div>
            <span className="tr-header__label">In progress</span>
            <h1>{attempt?.assessment_title}</h1>
          </div>
        </div>
        <div className={`tr-timer ${timerTone}`}>
          <FaClock />
          <span>{mm}:{ss}</span>
        </div>
      </header>

      <div className="tr-progress">
        <div className="tr-progress__bar">
          <div className="tr-progress__fill" style={{ width: `${progressPct}%` }} />
        </div>
        <span className="tr-progress__text">
          Question {index + 1} of {total}
        </span>
      </div>

      <main className="tr-body">
        {question && (
          <div className="tr-question">
            <p className="tr-question__text">{question.text}</p>
            {renderInput()}
          </div>
        )}

        <div className="tr-nav">
          <button
            type="button"
            className="tr-btn tr-btn--ghost"
            disabled={index === 0}
            onClick={() => setIndex((i) => Math.max(0, i - 1))}
          >
            Previous
          </button>

          {index < total - 1 ? (
            <button
              type="button"
              className="tr-btn tr-btn--primary"
              onClick={() => setIndex((i) => Math.min(total - 1, i + 1))}
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              className="tr-btn tr-btn--primary"
              onClick={() => setConfirming(true)}
            >
              <FaCheckCircle /> Submit
            </button>
          )}
        </div>
      </main>

      {confirming && (
        <div className="tr-modal" role="dialog" aria-modal="true">
          <div className="tr-modal__card">
            <h3>Submit your answers?</h3>
            <p>You won&apos;t be able to change them after submitting.</p>
            <div className="tr-modal__actions">
              <button
                type="button"
                className="tr-btn tr-btn--ghost"
                onClick={() => setConfirming(false)}
              >
                Keep going
              </button>
              <button
                type="button"
                className="tr-btn tr-btn--primary"
                onClick={() => submit(false)}
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestRunner;
''')


# ------------------------------------------------------------------
# 12. React — TestResult.jsx
# ------------------------------------------------------------------
print("\n[12/15] React — TestResult.jsx")

write(f"{REACT_SRC}/components/provider/TestResult.jsx", r'''
// src/components/provider/TestResult.jsx
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { FaCheckCircle, FaTimesCircle, FaCircleNotch } from 'react-icons/fa';
import api from '../../api/client';
import './TestCentre.css';

export const TestResult = () => {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .get(`/provider/attempts/${id}/result/`)
      .then((r) => setResult(r.data))
      .catch((err) =>
        setError(err?.response?.data?.detail || 'Could not load the result.')
      );
  }, [id]);

  if (error) {
    return (
      <div className="tr-page">
        <div className="tc-error">{error}</div>
        <Link to="/provider/test-centre" className="tc-back">Back to Test Centre</Link>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="tr-page">
        <div className="tc-loading">
          <FaCircleNotch className="tc-spin" /> Loading your result…
        </div>
      </div>
    );
  }

  const passed = result.passed;
  const tone = passed ? 'success' : 'fail';

  return (
    <div className="tr-page tr-page--result">
      <div className={`tr-result tr-result--${tone}`}>
        <div className="tr-result__icon">
          {passed ? <FaCheckCircle /> : <FaTimesCircle />}
        </div>
        <h1>{passed ? 'You passed!' : 'Not quite there yet'}</h1>
        <p className="tr-result__sub">
          {result.assessment_title}
        </p>

        <div className="tr-result__score">
          <span className="tr-result__score-value">{result.score}%</span>
          <span className="tr-result__score-label">
            Pass threshold: {result.pass_threshold}%
          </span>
        </div>

        <div className="tr-result__stats">
          <div>
            <span className="tr-result__stat-label">Duration</span>
            <span className="tr-result__stat-value">
              {Math.round(result.duration_seconds / 60)} min
            </span>
          </div>
          <div>
            <span className="tr-result__stat-label">Kind</span>
            <span className="tr-result__stat-value">{result.kind}</span>
          </div>
          {result.timed_out && (
            <div>
              <span className="tr-result__stat-label">Status</span>
              <span className="tr-result__stat-value">Timed out</span>
            </div>
          )}
        </div>

        {result.skill_unlocked && (
          <div className="tr-result__unlock">
            <FaCheckCircle />
            <div>
              <strong>Skill unlocked: {result.skill_unlocked.name}</strong>
              <span>You can now be assigned jobs in this category.</span>
            </div>
          </div>
        )}

        <div className="tr-result__actions">
          <Link to="/provider/test-centre" className="tr-btn tr-btn--ghost">
            Back to Test Centre
          </Link>
          {!passed && (
            <Link
              to={`/provider/test-centre/${result.assessment_slug}/run`}
              className="tr-btn tr-btn--primary"
            >
              Try again
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default TestResult;
''')


# ------------------------------------------------------------------
# 13. React CSS
# ------------------------------------------------------------------
print("\n[13/15] React — TestCentre.css")

write(f"{REACT_SRC}/components/provider/TestCentre.css", r'''
/* =========================================================
   Ayuda Test Centre (React)
   ========================================================= */

:root {
  color-scheme: light;
  --tc-bg: #f2f4fb;
  --tc-surface: #ffffff;
  --tc-ink-900: #0b1226;
  --tc-ink-700: #334155;
  --tc-ink-500: #64748b;
  --tc-ink-300: #cbd5e1;
  --tc-line: #e8ecf5;
  --tc-blue: #0a35d6;
  --tc-blue-600: #0030b8;
  --tc-blue-soft: #eef1fb;
  --tc-green: #10b981;
  --tc-green-soft: #eaf6f2;
  --tc-orange: #f59e0b;
  --tc-orange-soft: #fef3e2;
  --tc-red: #ef4444;
  --tc-radius-xl: 28px;
  --tc-radius-lg: 22px;
  --tc-radius-md: 16px;
  --tc-radius-sm: 12px;
  --tc-shadow-sm: 0 2px 10px -4px rgba(15, 23, 42, 0.08);
  --tc-shadow-md: 0 10px 30px -16px rgba(15, 23, 42, 0.15);
  --tc-font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

@media (prefers-color-scheme: dark) { :root { color-scheme: light; } }

/* ---------- Layout ---------- */
.tc-layout {
  display: grid;
  grid-template-columns: 288px 1fr;
  min-height: 100vh;
  background: var(--tc-bg);
  font-family: var(--tc-font);
  color: var(--tc-ink-900);
}
.tc-main { padding: 32px clamp(20px, 3vw, 48px) 48px; min-width: 0; }
.tc-inner { max-width: 1080px; display: flex; flex-direction: column; gap: 26px; }

/* ---------- Sidebar (shared with dashboard) ---------- */
.ay-sidebar {
  position: sticky; top: 0; height: 100vh; margin: 16px 0 16px 16px;
  padding: 32px 22px 22px; background: #fff;
  border: 1px solid var(--tc-line); border-radius: var(--tc-radius-xl);
  display: flex; flex-direction: column; gap: 28px; overflow-y: auto;
}
.ay-sidebar__brand { padding: 4px 8px; }
.ay-sidebar__logo { display: flex; align-items: baseline; gap: 2px; }
.ay-sidebar__logo-mark {
  width: 22px; height: 22px; border-radius: 50%;
  border: 5px solid var(--tc-blue); position: relative; top: 2px;
}
.ay-sidebar__logo-text {
  font-size: 34px; font-weight: 800; letter-spacing: -1.4px;
  color: var(--tc-blue); margin-left: -2px;
}
.ay-sidebar__brand-sub { margin: 2px 0 0; font-size: 11px; color: var(--tc-ink-500); }
.ay-sidebar__brand-title {
  margin: 20px 0 0; font-size: 11.5px; font-weight: 700;
  letter-spacing: 1.6px; text-transform: uppercase; color: var(--tc-ink-500);
}
.ay-nav { display: flex; flex-direction: column; gap: 2px; }
.ay-nav__item {
  position: relative; display: flex; align-items: center; gap: 16px;
  padding: 16px 18px; border-radius: 16px; font-size: 14px; font-weight: 800;
  letter-spacing: 1.2px; text-transform: uppercase;
  color: var(--tc-ink-900); text-decoration: none;
  transition: color 0.2s ease, background 0.2s ease, transform 0.15s ease;
  isolation: isolate;
}
.ay-nav__icon { display: grid; place-items: center; width: 22px; height: 22px;
  font-size: 18px; color: currentColor; flex-shrink: 0; }
.ay-nav__label { flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ay-nav__item:hover { color: var(--tc-blue); transform: translateX(2px); }
.ay-nav__item.is-active {
  background: linear-gradient(135deg, #0a35d6 0%, #1a4dff 100%);
  color: #fff;
  box-shadow: 0 18px 34px -16px rgba(10, 53, 214, 0.85),
              0 24px 60px -28px rgba(26, 77, 255, 0.7);
}
.ay-nav__item.is-active::after {
  content: ''; position: absolute; right: 18px; top: 50%;
  transform: translateY(-50%); width: 5px; height: 5px;
  border-radius: 50%; background: #fff;
}
.ay-nav__item.is-locked { color: var(--tc-ink-300); cursor: not-allowed; }
.ay-nav__item.is-locked:hover { color: var(--tc-ink-300); transform: none; }
.ay-nav__lock { font-size: 13px; color: var(--tc-ink-300); }

.ay-sidebar__footer {
  margin-top: auto; display: flex; align-items: center; gap: 12px;
  padding: 16px 12px 4px; border-top: 1px solid var(--tc-line);
}
.ay-sidebar__avatar {
  position: relative; width: 44px; height: 44px; border-radius: 50%;
  overflow: visible; background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff; display: grid; place-items: center; font-size: 16px; font-weight: 600; flex-shrink: 0;
}
.ay-sidebar__avatar img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.ay-sidebar__avatar-dot {
  position: absolute; right: -1px; bottom: -1px; width: 12px; height: 12px;
  border-radius: 50%; background: #10b981; border: 2px solid #fff;
}
.ay-sidebar__profile { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.ay-sidebar__profile strong {
  font-size: 13.5px; font-weight: 700; color: var(--tc-ink-900);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ay-sidebar__profile span { font-size: 12px; color: var(--tc-ink-500); }
.ay-sidebar__chev {
  display: grid; place-items: center; width: 34px; height: 34px;
  border-radius: 10px; border: 1px solid var(--tc-line);
  background: #fff; color: var(--tc-ink-500); font-size: 12px;
  cursor: pointer; transition: all 0.2s ease;
}
.ay-sidebar__chev:hover { background: #fff5f5; border-color: rgba(239, 68, 68, 0.35); color: #ef4444; }

/* ---------- Hero ---------- */
.tc-hero { padding: 4px 0 8px; }
.tc-hero__icon {
  width: 56px; height: 56px; border-radius: 18px;
  display: grid; place-items: center;
  background: linear-gradient(135deg, #0a35d6, #1a4dff);
  color: #fff; font-size: 24px;
  box-shadow: 0 18px 34px -16px rgba(10, 53, 214, 0.75);
  margin-bottom: 18px;
}
.tc-hero h1 {
  margin: 0 0 8px; font-size: clamp(30px, 3.5vw, 42px);
  font-weight: 800; letter-spacing: -1.2px; line-height: 1.05;
}
.tc-hero p { margin: 0; font-size: 15.5px; line-height: 1.55; color: var(--tc-ink-500); max-width: 720px; }

/* ---------- Section ---------- */
.tc-section { display: flex; flex-direction: column; gap: 16px; }
.tc-section__head { display: flex; align-items: flex-start; gap: 14px; }
.tc-section__icon {
  flex-shrink: 0; width: 40px; height: 40px; border-radius: 12px;
  display: grid; place-items: center;
  background: var(--tc-blue-soft); color: var(--tc-blue); font-size: 17px;
}
.tc-section__icon--bolt { background: var(--tc-orange-soft); color: var(--tc-orange); }
.tc-section__head h2 { margin: 0; font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
.tc-section__sub { margin: 4px 0 0; font-size: 13.5px; color: var(--tc-ink-500); }

/* ---------- Card ---------- */
.tc-card {
  display: flex; flex-direction: column; gap: 16px;
  padding: 24px 26px; background: var(--tc-surface);
  border: 1.5px solid var(--tc-line); border-radius: var(--tc-radius-lg);
  box-shadow: var(--tc-shadow-sm);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.tc-card:hover { transform: translateY(-2px); box-shadow: var(--tc-shadow-md); border-color: #d6ddec; }
.tc-card__head { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.tc-card__title { margin: 0; font-size: 17px; font-weight: 800; letter-spacing: -0.3px; }
.tc-card__desc { margin: 0; font-size: 14px; line-height: 1.6; color: var(--tc-ink-500); max-width: 780px; }

.tc-status {
  display: inline-flex; align-items: center;
  font-size: 11px; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase;
  padding: 6px 12px; border-radius: 999px; flex-shrink: 0;
}
.tc-status--success { color: #06795f; background: var(--tc-green-soft); border: 1px solid #c1e5da; }
.tc-status--ready { color: var(--tc-blue-600); background: var(--tc-blue-soft); border: 1px solid #cdd7f5; }
.tc-status--locked { color: var(--tc-ink-500); background: #f1f4f9; border: 1px solid var(--tc-line); }

.tc-card__meta {
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px;
  padding: 16px; border-radius: var(--tc-radius-md);
  background: #f8fafc; border: 1px solid var(--tc-line);
}
.tc-meta { display: flex; flex-direction: column; gap: 4px; }
.tc-meta__label {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase;
  color: var(--tc-ink-500);
}
.tc-meta__label svg { font-size: 11px; color: var(--tc-blue); }
.tc-meta__value { font-size: 16px; font-weight: 800; letter-spacing: -0.3px; }

.tc-cta {
  align-self: stretch; display: inline-flex; align-items: center; justify-content: center;
  gap: 8px; padding: 14px 20px; font: inherit;
  font-size: 13px; font-weight: 800; letter-spacing: 1.4px; text-transform: uppercase;
  border-radius: var(--tc-radius-md); border: 0; cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.tc-cta--success { background: var(--tc-green-soft); color: #06795f; border: 1.5px solid #c1e5da; }
.tc-cta--success:hover { transform: translateY(-1px); }
.tc-cta--ready {
  background: linear-gradient(135deg, #0a35d6, #1a4dff); color: #fff;
  box-shadow: 0 14px 28px -14px rgba(10, 53, 214, 0.75);
}
.tc-cta--ready:hover { transform: translateY(-1px); box-shadow: 0 20px 34px -16px rgba(10, 53, 214, 0.85); }
.tc-cta--locked { background: #f1f4f9; color: var(--tc-ink-300); cursor: not-allowed; border: 1.5px solid var(--tc-line); }
.tc-cta:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

.tc-skill-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 16px; }

/* Locked / empty / error / loading */
.tc-locked {
  display: flex; align-items: flex-start; gap: 16px;
  padding: 22px 24px; border-radius: var(--tc-radius-lg);
  background: #f8fafc; border: 1.5px dashed #d6ddec;
}
.tc-locked__icon {
  flex-shrink: 0; width: 46px; height: 46px; border-radius: 14px;
  display: grid; place-items: center;
  background: #fff; color: var(--tc-ink-300); font-size: 18px; border: 1px solid var(--tc-line);
}
.tc-locked strong { display: block; font-size: 15px; font-weight: 800; margin-bottom: 4px; }
.tc-locked p { margin: 0; font-size: 13.5px; color: var(--tc-ink-500); line-height: 1.5; }

.tc-empty, .tc-error, .tc-loading {
  padding: 24px; text-align: center; font-size: 14px;
  border-radius: var(--tc-radius-md);
  border: 1px dashed var(--tc-line);
  color: var(--tc-ink-500); background: #fff;
}
.tc-error { color: #b91c1c; border-color: #fecaca; background: #fef2f2; }
.tc-loading { display: flex; align-items: center; justify-content: center; gap: 10px; }
.tc-spin { animation: tc-spin 0.8s linear infinite; }
@keyframes tc-spin { to { transform: rotate(360deg); } }

/* Help */
.tc-help {
  display: flex; align-items: center; justify-content: space-between; gap: 20px;
  padding: 24px 26px; background: var(--tc-surface);
  border: 1.5px solid var(--tc-line); border-radius: var(--tc-radius-lg);
  box-shadow: var(--tc-shadow-sm); flex-wrap: wrap;
}
.tc-help__left { display: flex; align-items: flex-start; gap: 14px; min-width: 0; flex: 1; }
.tc-help__icon {
  flex-shrink: 0; width: 46px; height: 46px; border-radius: 14px;
  display: grid; place-items: center;
  background: var(--tc-blue-soft); color: var(--tc-blue); font-size: 18px;
}
.tc-help__left strong { display: block; font-size: 15px; font-weight: 800; margin-bottom: 4px; }
.tc-help__left p { margin: 0; font-size: 13.5px; line-height: 1.5; color: var(--tc-ink-500); max-width: 620px; }
.tc-help__btn {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 13px 22px; font: inherit; font-size: 13px; font-weight: 800;
  letter-spacing: 1.2px; text-transform: uppercase;
  border-radius: var(--tc-radius-md); background: linear-gradient(135deg, #0a35d6, #1a4dff);
  color: #fff; text-decoration: none;
  box-shadow: 0 14px 28px -14px rgba(10, 53, 214, 0.75);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}
.tc-help__btn:hover { transform: translateY(-1px); }

/* ---------- Test runner ---------- */
.tr-page { min-height: 100vh; background: var(--tc-bg); padding: 32px clamp(16px, 3vw, 40px); font-family: var(--tc-font); }
.tr-header {
  display: flex; align-items: center; justify-content: space-between; gap: 20px;
  max-width: 900px; margin: 0 auto 20px;
  padding: 20px 26px; background: #fff;
  border: 1px solid var(--tc-line); border-radius: var(--tc-radius-lg);
  box-shadow: var(--tc-shadow-sm); flex-wrap: wrap;
}
.tr-header__left { display: flex; align-items: center; gap: 14px; }
.tr-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--tc-blue);
  box-shadow: 0 0 0 6px rgba(10, 53, 214, 0.15); }
.tr-header__label { font-size: 11px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: var(--tc-blue); }
.tr-header h1 { margin: 2px 0 0; font-size: 18px; font-weight: 800; letter-spacing: -0.3px; }
.tr-timer {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 16px; border-radius: 999px;
  background: var(--tc-blue-soft); color: var(--tc-blue-600);
  font-size: 14px; font-weight: 800; font-variant-numeric: tabular-nums;
}
.tr-timer.warning { background: #fef3c7; color: #92400e; }
.tr-timer.danger { background: #fee2e2; color: #991b1b; animation: tr-pulse 1s ease-in-out infinite; }
@keyframes tr-pulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.05); } }

.tr-progress { max-width: 900px; margin: 0 auto 22px; }
.tr-progress__bar { height: 8px; background: #e2e8f2; border-radius: 999px; overflow: hidden; }
.tr-progress__fill { height: 100%; background: linear-gradient(90deg, #0a35d6, #1a4dff); border-radius: 999px; transition: width 0.3s ease; }
.tr-progress__text { display: block; margin-top: 8px; font-size: 12.5px; font-weight: 600; color: var(--tc-ink-500); }

.tr-body { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }
.tr-question { padding: 32px 30px; background: #fff; border: 1px solid var(--tc-line); border-radius: var(--tc-radius-lg); box-shadow: var(--tc-shadow-sm); }
.tr-question__text { margin: 0 0 24px; font-size: 20px; font-weight: 700; letter-spacing: -0.3px; line-height: 1.4; color: var(--tc-ink-900); }

.tr-options { display: grid; gap: 12px; }
.tr-option {
  padding: 16px 20px; text-align: left; font: inherit; font-size: 14.5px; font-weight: 500;
  border-radius: var(--tc-radius-md); border: 1.5px solid var(--tc-line); background: #fff;
  color: var(--tc-ink-900); cursor: pointer; transition: all 0.2s ease;
}
.tr-option:hover { border-color: var(--tc-blue); background: #f8fafc; }
.tr-option.is-selected { border-color: var(--tc-blue); background: var(--tc-blue-soft); color: var(--tc-blue-600); font-weight: 700;
  box-shadow: 0 0 0 4px rgba(10, 53, 214, 0.08); }

.tr-likert { display: flex; gap: 12px; flex-wrap: wrap; }
.tr-likert__opt {
  flex: 1; min-width: 56px; padding: 16px;
  font: inherit; font-size: 16px; font-weight: 800;
  border-radius: var(--tc-radius-md); border: 1.5px solid var(--tc-line);
  background: #fff; color: var(--tc-ink-700); cursor: pointer; transition: all 0.2s ease;
}
.tr-likert__opt:hover { border-color: var(--tc-blue); }
.tr-likert__opt.is-selected { background: linear-gradient(135deg, #0a35d6, #1a4dff); color: #fff; border-color: transparent;
  box-shadow: 0 12px 24px -12px rgba(10, 53, 214, 0.7); }

.tr-nav { display: flex; justify-content: space-between; gap: 12px; }

.tr-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  padding: 14px 24px; font: inherit; font-size: 14px; font-weight: 700;
  border-radius: var(--tc-radius-md); border: 1.5px solid transparent; cursor: pointer;
  transition: all 0.2s ease;
}
.tr-btn--primary { background: linear-gradient(135deg, #0a35d6, #1a4dff); color: #fff;
  box-shadow: 0 14px 28px -14px rgba(10, 53, 214, 0.75); }
.tr-btn--primary:hover { transform: translateY(-1px); }
.tr-btn--ghost { background: #fff; border-color: var(--tc-line); color: var(--tc-ink-700); }
.tr-btn--ghost:hover:not(:disabled) { border-color: var(--tc-blue); color: var(--tc-blue); }
.tr-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.tr-modal {
  position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4);
  display: grid; place-items: center; z-index: 50; padding: 20px;
}
.tr-modal__card {
  max-width: 420px; width: 100%; padding: 28px;
  background: #fff; border-radius: var(--tc-radius-lg);
  box-shadow: 0 30px 80px -30px rgba(15, 23, 42, 0.45);
}
.tr-modal__card h3 { margin: 0 0 8px; font-size: 18px; font-weight: 800; }
.tr-modal__card p { margin: 0 0 20px; font-size: 14px; color: var(--tc-ink-500); line-height: 1.5; }
.tr-modal__actions { display: flex; gap: 10px; justify-content: flex-end; }

/* ---------- Result ---------- */
.tr-page--result { display: grid; place-items: center; padding: 48px 20px; }
.tr-result {
  max-width: 520px; width: 100%; text-align: center;
  padding: 48px 40px; background: #fff;
  border-radius: var(--tc-radius-lg); border: 1px solid var(--tc-line);
  box-shadow: var(--tc-shadow-md);
}
.tr-result__icon { font-size: 56px; margin-bottom: 16px; }
.tr-result--success .tr-result__icon { color: var(--tc-green); }
.tr-result--fail .tr-result__icon { color: var(--tc-red); }
.tr-result h1 { margin: 0 0 6px; font-size: 26px; font-weight: 800; letter-spacing: -0.6px; }
.tr-result__sub { margin: 0 0 24px; font-size: 14px; color: var(--tc-ink-500); }
.tr-result__score {
  display: inline-flex; flex-direction: column; gap: 4px;
  padding: 20px 36px; border-radius: var(--tc-radius-md);
  background: #f8fafc; border: 1px solid var(--tc-line); margin-bottom: 20px;
}
.tr-result__score-value { font-size: 42px; font-weight: 800; letter-spacing: -1.5px; color: var(--tc-ink-900); }
.tr-result__score-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; color: var(--tc-ink-500); }
.tr-result__stats { display: flex; gap: 22px; justify-content: center; margin-bottom: 24px; flex-wrap: wrap; }
.tr-result__stats > div { display: flex; flex-direction: column; gap: 2px; }
.tr-result__stat-label { font-size: 11px; font-weight: 700; letter-spacing: 0.6px; text-transform: uppercase; color: var(--tc-ink-500); }
.tr-result__stat-value { font-size: 15px; font-weight: 700; color: var(--tc-ink-900); text-transform: capitalize; }
.tr-result__unlock {
  display: flex; align-items: center; gap: 12px; text-align: left;
  padding: 16px; border-radius: var(--tc-radius-md);
  background: var(--tc-green-soft); border: 1px solid #c1e5da; margin-bottom: 24px;
}
.tr-result__unlock > svg { color: var(--tc-green); font-size: 22px; flex-shrink: 0; }
.tr-result__unlock strong { display: block; font-size: 13.5px; font-weight: 800; color: #065f46; }
.tr-result__unlock span { font-size: 12px; color: #047857; }
.tr-result__actions { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }

.tc-back { display: inline-block; margin-top: 20px; color: var(--tc-blue); font-weight: 700; text-decoration: none; }

/* ---------- Responsive ---------- */
@media (max-width: 1100px) {
  .tc-layout { grid-template-columns: 1fr; }
  .ay-sidebar { position: relative; height: auto; margin: 12px; border-radius: var(--tc-radius-lg); }
  .ay-nav { flex-direction: row; overflow-x: auto; gap: 8px; padding-bottom: 4px; }
  .ay-nav__item { flex-shrink: 0; padding: 12px 14px; }
  .ay-nav__label { display: none; }
  .ay-nav__item.is-active .ay-nav__label { display: inline; }
}
@media (max-width: 900px) { .tc-skill-grid { grid-template-columns: 1fr; } }
@media (max-width: 640px) {
  .tc-main { padding: 20px 16px 32px; }
  .tc-card__meta { grid-template-columns: 1fr; }
  .tc-help { flex-direction: column; align-items: stretch; }
  .tc-help__btn { width: 100%; }
  .tr-nav { flex-direction: column-reverse; }
  .tr-btn { width: 100%; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.001ms !important; transition-duration: 0.001ms !important; }
}
''')


# ------------------------------------------------------------------
# 14. Wire into Django settings + urls
# ------------------------------------------------------------------
print("\n[14/15] Wiring Django settings + urls")

settings_path = find_settings()
if settings_path:
    # Add "provider" to INSTALLED_APPS
    p = ROOT / settings_path
    text = p.read_text(encoding="utf-8")
    if '"provider"' not in text and "'provider'" not in text:
        # Try to insert after the last app line
        pattern = re.compile(r'(INSTALLED_APPS\s*=\s*\[[^\]]*?)(\n\])', re.DOTALL)
        m = pattern.search(text)
        if m:
            insert_at = m.end(1)
            new_text = (
                text[:insert_at]
                + '    "provider",\n'
                + text[insert_at:]
            )
            backup(settings_path)
            p.write_text(new_text, encoding="utf-8")
            print(f"  updated {settings_path} (added provider to INSTALLED_APPS)")
        else:
            print(f"  !!      {settings_path}: INSTALLED_APPS pattern not found")
    else:
        print(f"  skip    {settings_path} (provider already in INSTALLED_APPS)")
else:
    print("  !!      settings.py not found — add 'provider' to INSTALLED_APPS manually")

urls_path = find_root_urls()
if urls_path and (ROOT / urls_path).exists():
    p = ROOT / urls_path
    text = p.read_text(encoding="utf-8")

    if 'provider.urls' in text:
        print(f"  skip    {urls_path} (provider.urls already included)")
    else:
        # Ensure include is imported
        if "from django.urls import" in text and "include" not in text.split("from django.urls import")[1].split("\n")[0]:
            text = text.replace(
                "from django.urls import",
                "from django.urls import include,",
                1,
            )
        # Insert the include before the last ]
        include_line = '    path("api/provider/", include("provider.urls", namespace="provider")),\n'
        inserted = False
        for needle in ("\n]", "\r\n]", "\n]\n"):
            if needle in text:
                text = text.replace(needle, include_line + needle, 1)
                inserted = True
                break
        if inserted:
            backup(urls_path)
            p.write_text(text, encoding="utf-8")
            print(f"  updated {urls_path} (added /api/provider/)")
        else:
            print(f"  !!      {urls_path}: no closing bracket found")
else:
    print(f"  !!      root urls not found — add include('provider.urls') manually")


# ------------------------------------------------------------------
# 15. Print integration snippet for App.jsx
# ------------------------------------------------------------------
print("\n[15/15] App.jsx integration snippet")

snippet = """
/* Add these routes to your React router (e.g. src/App.jsx or routes.jsx): */
import TestCentre from './components/provider/TestCentre';
import TestRunner from './components/provider/TestRunner';
import TestResult from './components/provider/TestResult';

<Route path="/provider/test-centre" element={<TestCentre />} />
<Route path="/provider/test-centre/:slug/run" element={<TestRunner />} />
<Route path="/provider/test-centre/result/:id" element={<TestResult />} />
"""

print(snippet)


# ==================================================================
# DONE
# ==================================================================
print("""
=== Done ===

Next steps:

1. Backend:
       python manage.py makemigrations provider
       python manage.py migrate
       python manage.py seed_test_centre
       python manage.py runserver

2. Add the routes to your React router (see snippet above).

3. (Optional) Make sure your axios instance points at the Django API:
       src/api/client.js should have baseURL: "http://localhost:8000/api"

4. Verify:
       - Log in as an artisan
       - Visit /provider/test-centre
       - You should see the psychometric test (READY), skill tests (LOCKED)
       - Take the psychometric → unlocked skill tests
       - Take a skill test → ArtisanSkill row created

Notes:
  - The scoring is fully server-side. The frontend never sees `correct`.
  - Attempts are locked with select_for_update — no double-start races.
  - If a run exceeds the duration, the submit view marks it `timed_out`.
  - To reset attempts: /api/provider/assessments/<slug>/reset/  (staff only)
""")
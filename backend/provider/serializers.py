
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

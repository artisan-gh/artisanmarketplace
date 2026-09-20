
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

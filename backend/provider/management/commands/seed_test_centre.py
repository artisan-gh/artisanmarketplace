
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

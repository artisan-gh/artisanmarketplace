
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

from django.contrib import admin
from django.utils import timezone
from .models import Organization, OrganizationMember, OrganizationInvite


class OrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    extra = 1
    fields = ["user", "role", "is_active"]
    raw_id_fields = ["user"]


class OrganizationInviteInline(admin.TabularInline):
    model = OrganizationInvite
    extra = 1
    fields = ["email", "role", "status", "token", "expires_at"]
    readonly_fields = ["token", "expires_at"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "email", "phone", "tax_id")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [OrganizationMemberInline, OrganizationInviteInline]
    fieldsets = (
        (None, {
            "fields": ("name", "email", "phone", "address")
        }),
        ("Details", {
            "fields": ("website", "tax_id", "is_active")
        }),
        ("Audit", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "is_active", "joined_at")
    list_filter = ("role", "is_active", "organization")
    search_fields = ("user__email", "user__first_name", "user__last_name", "organization__name")
    readonly_fields = ("joined_at",)
    raw_id_fields = ["user"]


@admin.register(OrganizationInvite)
class OrganizationInviteAdmin(admin.ModelAdmin):
    list_display = ("email", "organization", "role", "status", "expires_at", "is_expired")
    list_filter = ("status", "role", "organization")
    search_fields = ("email", "organization__name")
    readonly_fields = ("token", "created_at")
    raw_id_fields = ["invited_by"]

    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = "Expired?"

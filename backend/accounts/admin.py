# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django import forms
from django.utils.html import format_html
from django.conf import settings
import os

from .models import (
    User,
    LoginHistory,
    UserSession,
    AgentProfile,
    SupervisorProfile,
    DispatcherProfile,
    ManagerProfile,
    CompanyProfile,
    AdminProfile,
    EmployeeSequence,
)


# ------------------------------------------------------------
# PROFILE INLINE CLASSES
# ------------------------------------------------------------
class AgentProfileInline(admin.StackedInline):
    model = AgentProfile
    can_delete = False
    verbose_name_plural = "Agent Profile"
    fk_name = 'user'
    fields = ('extension', 'is_active', 'assigned_queue')
    extra = 0


class SupervisorProfileInline(admin.StackedInline):
    model = SupervisorProfile
    can_delete = False
    verbose_name_plural = "Supervisor Profile"
    fk_name = 'user'
    fields = ('team_size', 'is_active')
    extra = 0


class DispatcherProfileInline(admin.StackedInline):
    model = DispatcherProfile
    can_delete = False
    verbose_name_plural = "Dispatcher Profile"
    fk_name = 'user'
    fields = ('is_active',)
    extra = 0


class ManagerProfileInline(admin.StackedInline):
    model = ManagerProfile
    can_delete = False
    verbose_name_plural = "Manager Profile"
    fk_name = 'user'
    fields = ('is_active', 'department')
    extra = 0


class CompanyProfileInline(admin.StackedInline):
    model = CompanyProfile
    can_delete = False
    verbose_name_plural = "Company Profile"
    fk_name = 'user'
    fields = ('company_name', 'is_active')
    extra = 0


class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = "Admin Profile"
    fk_name = 'user'
    fields = ('is_active',)
    extra = 0


# ------------------------------------------------------------
# CUSTOM USER ADMIN FORM (optional – for validation)
# ------------------------------------------------------------
class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower()
            # Check uniqueness (excluding self)
            qs = User.objects.exclude(pk=self.instance.pk).filter(email=email)
            if qs.exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email


# ------------------------------------------------------------
# CUSTOM USER ADMIN
# ------------------------------------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom Admin for the User model.
    - Uses email as the unique identifier (username field is removed).
    - Organizes fields into logical sections.
    - Includes groups and permissions inlines.
    - Adds custom actions for soft-delete, activate, etc.
    - Displays profile picture and proof of address as images.
    """
    form = UserAdminForm

    list_display = (
        "id",
        "email",
        "full_name",
        "user_type",
        "employee_number",
        "account_status",
        "is_active",
        "is_verified",
        "is_online",
        "last_seen",
        "profile_picture_preview",   # added
        "created_at",
    )
    list_filter = (
        "user_type",
        "account_status",
        "is_active",
        "is_verified",
        "is_deleted",
        "is_online",
        "gender",
        "department",
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "employee_number",
        "identification_number",
        "introduction",
        "nationality",
        "education",
        "interests",
        "languages",
        "employer",
        "whatsapp",
        "facebook",
        "instagram",
        "twitter",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "id",
        "employee_number",
        "last_login",
        "last_login_ip",
        "last_seen",
        "created_at",
        "updated_at",
        "deleted_at",
        "is_online",
        "profile_picture_preview",   # added
        "proof_of_address_preview",  # added
    )
    list_per_page = 25

    # ─── Dynamic inlines based on user_type ──────────────
    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.user_type == User.UserType.AGENT:
            return [AgentProfileInline]
        elif obj.user_type == User.UserType.SUPERVISOR:
            return [SupervisorProfileInline]
        elif obj.user_type == User.UserType.DISPATCHER:
            return [DispatcherProfileInline]
        elif obj.user_type == User.UserType.MANAGER:
            return [ManagerProfileInline]
        elif obj.user_type == User.UserType.COMPANY:
            return [CompanyProfileInline]
        elif obj.user_type == User.UserType.ADMIN:
            return [AdminProfileInline]
        # ARTISAN profiles are handled in the artisans app
        return []

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Information"), {
            "fields": (
                "first_name",
                "last_name",
                "phone_number",
                "date_of_birth",
                "gender",
                "profile_picture",
                "profile_picture_preview",   # readonly preview
            )
        }),
        # ─── NEW: Profile Details ──────────────────────────
        (_("Profile Details"), {
            "fields": (
                "introduction",
                "nationality",
                "education",
                "interests",
                "languages",
                "employer",
            )
        }),
        # ─── NEW: Social Media ─────────────────────────────
        (_("Social Media"), {
            "fields": (
                "whatsapp",
                "facebook",
                "instagram",
                "twitter",
            )
        }),
        (_("Employment Details"), {
            "fields": (
                "user_type",
                "employee_number",
                "department",
                "job_title",
                "hire_date",
            )
        }),
        (_("KYC & Verification"), {
            "fields": (
                "identification_document_type",
                "identification_number",
                "proof_of_address",
                "proof_of_address_preview",   # readonly preview
                "is_verified",
                "email_verified",
                "phone_verified",
            )
        }),
        (_("Account Status"), {
            "fields": (
                "account_status",
                "is_active",
                "is_deleted",
                "deleted_at",
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (_("Online Presence"), {
            "fields": (
                "is_online",
                "last_seen",
            )
        }),
        (_("Emergency Contact"), {
            "fields": (
                "emergency_contact_name",
                "emergency_contact_phone",
            )
        }),
        (_("Preferences"), {
            "fields": ("timezone",)
        }),
        (_("Audit & Timestamps"), {
            "fields": (
                "id",
                "last_login",
                "last_login_ip",
                "created_at",
                "updated_at",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "first_name",
                "last_name",
                "phone_number",
                "user_type",
                "account_status",
            )
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "username" in form.base_fields:
            form.base_fields.pop("username")
        return form

    @admin.display(description="Full Name", ordering="first_name")
    def full_name(self, obj):
        return obj.get_full_name()

    # ─── IMAGE PREVIEW METHODS ──────────────────────────────
    @admin.display(description="Profile Picture")
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            url = obj.profile_picture.url
            # Use a small thumbnail in the list view, and larger in detail
            # For detail, we can use the full size; we'll use a fixed width in list.
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius:50%; object-fit:cover;" />',
                url
            )
        return "—"

    @admin.display(description="Proof of Address")
    def proof_of_address_preview(self, obj):
        if obj.proof_of_address:
            url = obj.proof_of_address.url
            # Check if it's an image by extension
            ext = os.path.splitext(url)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                return format_html(
                    '<img src="{}" width="80" style="border:1px solid #ccc; border-radius:4px;" />',
                    url
                )
            else:
                # Show a download link
                return format_html(
                    '<a href="{}" target="_blank">📄 View/Download</a>',
                    url
                )
        return "—"

    # ─── ADMIN ACTIONS ──────────────────────────────────────
    @admin.action(description="Activate selected users (set status = ACTIVE)")
    def activate_users(self, request, queryset):
        updated = queryset.update(
            account_status=User.AccountStatus.ACTIVE,
            is_active=True,
            is_deleted=False,
        )
        self.message_user(request, f"{updated} users activated.")

    @admin.action(description="Soft-delete selected users")
    def soft_delete_users(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(
            is_active=False,
            is_deleted=True,
            deleted_at=now,
        )
        self.message_user(request, f"{updated} users soft-deleted.")

    @admin.action(description="Restore selected users (undelete)")
    def restore_users(self, request, queryset):
        updated = queryset.update(
            is_deleted=False,
            deleted_at=None,
            is_active=True,
            account_status=User.AccountStatus.ACTIVE,
        )
        self.message_user(request, f"{updated} users restored.")

    @admin.action(description="Mark as verified (KYC complete)")
    def mark_verified(self, request, queryset):
        updated = queryset.update(
            is_verified=True,
            account_status=User.AccountStatus.ACTIVE,
            is_active=True,
        )
        self.message_user(request, f"{updated} users marked as verified.")

    actions = [
        activate_users,
        soft_delete_users,
        restore_users,
        mark_verified,
    ]


# ------------------------------------------------------------
# REGISTER PROFILE MODELS INDEPENDENTLY
# ------------------------------------------------------------
@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'extension', 'is_active', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'team_size', 'is_active', 'created_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)


@admin.register(DispatcherProfile)
class DispatcherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_active', 'created_at')
    search_fields = ('user__email', 'department')
    raw_id_fields = ('user',)


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'is_active', 'created_at')
    search_fields = ('user__email', 'company_name')
    raw_id_fields = ('user',)


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)


# ------------------------------------------------------------
# EMPLOYEE SEQUENCE ADMIN (read-only)
# ------------------------------------------------------------
@admin.register(EmployeeSequence)
class EmployeeSequenceAdmin(admin.ModelAdmin):
    """
    Read-only admin to monitor the employee number counter.
    """
    list_display = ('year', 'current_number', 'next_number')
    search_fields = ('year',)
    ordering = ('-year',)
    readonly_fields = ('year', 'current_number', 'next_number')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Next Number")
    def next_number(self, obj):
        return obj.current_number + 1


# ------------------------------------------------------------
# LOGIN HISTORY ADMIN (read-only)
# ------------------------------------------------------------
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "ip_address",
        "device_name",
        "successful",
        "created_at",
    )
    list_filter = ("successful", "created_at", "user")
    search_fields = ("user__email", "ip_address", "device_name")
    readonly_fields = (
        "id",
        "user",
        "ip_address",
        "user_agent",
        "device_name",
        "browser",
        "operating_system",
        "successful",
        "failure_reason",
        "logout_time",
        "created_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ------------------------------------------------------------
# USER SESSION ADMIN (read-only + revoke action)
# ------------------------------------------------------------
@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "device_name",
        "ip_address",
        "created_at",
        "expires_at",
        "revoked",
        "is_expired",
    )
    list_filter = ("revoked", "created_at", "expires_at")
    search_fields = ("user__email", "device_name", "ip_address", "jti")
    readonly_fields = (
        "id",
        "user",
        "jti",
        "device_name",
        "ip_address",
        "user_agent",
        "browser",
        "operating_system",
        "expires_at",
        "revoked",
        "revoked_at",
        "created_at",
        "last_activity",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(boolean=True, description="Expired?")
    def is_expired(self, obj):
        return obj.is_expired

    @admin.action(description="Revoke selected sessions")
    def revoke_sessions(self, request, queryset):
        updated = 0
        for session in queryset:
            if not session.revoked:
                session.revoke()
                updated += 1
        self.message_user(request, f"{updated} sessions revoked.")

    actions = [revoke_sessions]

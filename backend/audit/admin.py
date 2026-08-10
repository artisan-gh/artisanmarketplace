# audit/admin.py
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "user",
        "action",
        "module",
        "object_repr",
        "success",
        "severity",
    ]
    list_filter = [
        "action",
        "severity",
        "module",
        "success",
        "archived",
        "created_at",
    ]
    search_fields = ["user__email", "module", "object_repr", "description"]

    # ✅ Correct readonly_fields – uses the actual model fields
    readonly_fields = (
        "id",
        "user",
        "action",
        "severity",
        "module",
        "content_type",
        "object_id",
        "object_repr",
        "old_values",
        "new_values",
        "success",
        "response_status",
        "duration_ms",
        "request_id",
        "correlation_id",
        "ip_address",
        "path",
        "method",
        "user_agent",
        "browser",
        "operating_system",
        "device",
        "description",
        "exception",
        "archived",
        "organization",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

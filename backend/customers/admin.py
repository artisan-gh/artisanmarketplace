from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Customer model.
    """
    list_display = (
        "name",
        "phone",
        "email",
        "organization",
        "created_at",
        "is_deleted",
        "created_by",
    )
    list_filter = (
        "is_deleted",
        "organization",
        "created_at",
        "created_by",
    )
    search_fields = (
        "name",
        "phone",
        "email",
        "address",
        "notes",
        "tags",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "deleted_at",
    )
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (None, {
            "fields": ("name", "phone", "email", "address")
        }),
        (_("Location"), {
            "fields": ("gps_lat", "gps_lng"),
            "classes": ("collapse",)
        }),
        (_("Organization"), {
            "fields": ("organization",)
        }),
        (_("Metadata"), {
            "fields": ("notes", "tags")
        }),
        (_("Audit & Soft Delete"), {
            "fields": (
                "id",
                "created_at",
                "updated_at",
                "created_by",
                "updated_by",
                "is_deleted",
                "deleted_at",
            ),
            "classes": ("collapse",)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        """
        When editing an existing object, make created_by/updated_by readonly.
        """
        if obj:  # editing
            return self.readonly_fields + ("created_by", "updated_by")
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """
        Auto-set created_by/updated_by.
        """
        if not change:  # new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    # ─── Custom Admin Actions ──────────────────────────────

    @admin.action(
        description="Soft-delete selected customers",
        permissions=["delete"]
    )
    def soft_delete_selected(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(is_deleted=True, deleted_at=now)
        self.message_user(request, f"{updated} customer(s) soft-deleted.")

    @admin.action(
        description="Restore selected customers",
        permissions=["delete"]
    )
    def restore_selected(self, request, queryset):
        updated = queryset.update(is_deleted=False, deleted_at=None)
        self.message_user(request, f"{updated} customer(s) restored.")

    @admin.action(
        description="Export selected customers as CSV",
        permissions=["view"]
    )
    def export_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="customers.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "ID", "Name", "Phone", "Email", "Address",
            "Organization", "Created At", "Is Deleted"
        ])
        for customer in queryset:
            writer.writerow([
                customer.id,
                customer.name,
                customer.phone,
                customer.email,
                customer.address,
                customer.organization.name if customer.organization else "",
                customer.created_at,
                "Yes" if customer.is_deleted else "No",
            ])
        return response

    actions = [
        soft_delete_selected,
        restore_selected,
        export_csv,
    ]

from django.contrib import admin
from django.utils.html import format_html
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "subcategory_display",
        "minimum_price",
        "maximum_price",
        "estimated_duration",
        "image_preview",
        "artisan_count_display",
        "is_featured",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "subcategory",
        "is_featured",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "category__name",
        "subcategory__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
        "artisan_count_display",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    ordering = (
        "category",
        "name",
    )

    list_select_related = (
        "category",
        "subcategory",
    )

    list_per_page = 25

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "category",
                    "subcategory",
                    "name",
                    "slug",
                    "description",
                    "image",
                    "image_preview",
                )
            },
        ),
        (
            "Pricing & Duration",
            {
                "fields": (
                    "minimum_price",
                    "maximum_price",
                    "estimated_duration",
                )
            },
        ),
        (
            "Marketplace",
            {
                "fields": (
                    "artisan_count_display",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_featured",
                    "is_active",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # ─── Custom methods ────────────────────────────────────────

    def subcategory_display(self, obj):
        return obj.subcategory.name if obj.subcategory else "-"
    subcategory_display.short_description = "Subcategory"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit:cover; border-radius:4px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Image"

    def artisan_count_display(self, obj):
        count = obj.artisan_offerings.count()
        if count:
            return format_html(
                '<a href="/admin/artisans/artisanservice/?service__id__exact={}" target="_blank">{} offering(s)</a>',
                obj.id,
                count
            )
        return "No artisans yet"
    artisan_count_display.short_description = "Artisans offering"

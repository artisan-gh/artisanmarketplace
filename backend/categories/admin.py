from django.contrib import admin

from .models import Category, SubCategory


# =============================================================================
# CATEGORY ADMIN
# =============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    ordering = (
        "name",
    )

    list_per_page = 20


# =============================================================================
# SUBCATEGORY ADMIN
# =============================================================================

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "category__name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "category",
        "name",
    )

    list_select_related = (
        "category",
    )

    list_per_page = 20

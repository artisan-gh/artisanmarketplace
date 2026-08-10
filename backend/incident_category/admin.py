from django.contrib import admin
from .models import IncidentCategory, SubCategory


class SubCategoryInline(admin.TabularInline):
    """
    Inline admin for subcategories, displayed inside the category edit page.
    """
    model = SubCategory
    extra = 1
    fields = ['code', 'name', 'is_active', 'ordering', 'description']
    readonly_fields = ['code']
    ordering = ['ordering', 'name']


@admin.register(IncidentCategory)
class IncidentCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'ordering', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description', 'code']
    ordering = ['ordering', 'name']
    readonly_fields = ['code']
    fields = ['code', 'name', 'description', 'is_active', 'ordering']
    inlines = [SubCategoryInline]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'is_active', 'ordering']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'description', 'code', 'category__name']
    ordering = ['category__name', 'ordering', 'name']
    readonly_fields = ['code']
    fields = ['code', 'category', 'name', 'description', 'is_active', 'ordering']
    raw_id_fields = ['category']  # useful if you have many categories

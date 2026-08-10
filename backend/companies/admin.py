from django.contrib import admin
from django.utils.html import format_html
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'registration_number',
        'owner',
        'members_count_display',
        'is_active',
        'is_verified',
        'created_at',
    )
    list_filter = ('is_active', 'is_verified', 'created_at')
    search_fields = ('name', 'registration_number', 'owner__email')
    readonly_fields = ('created_at', 'updated_at', 'logo_preview')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)

    fieldsets = (
        ('Company Info', {'fields': ('name', 'slug', 'registration_number', 'description', 'logo', 'logo_preview')}),
        ('Contact', {'fields': ('email', 'phone', 'website', 'address')}),
        ('Owner & Status', {'fields': ('owner', 'is_active', 'is_verified')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="80" style="object-fit:cover; border-radius:4px;" />',
                obj.logo.url
            )
        return "-"
    logo_preview.short_description = "Logo Preview"

    def members_count_display(self, obj):
        return obj.members_count
    members_count_display.short_description = "Members"

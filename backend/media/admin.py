from django.contrib import admin
from django.utils.html import format_html
from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'file_name', 'user', 'category', 'file_type',
        'file_size_display', 'preview', 'is_public', 'is_active', 'created_at'
    )
    list_filter = ('category', 'file_type', 'is_public', 'is_active', 'created_at')
    search_fields = ('file_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'file_size', 'mime_type', 'width', 'height', 'preview')
    ordering = ('-created_at',)

    fieldsets = (
        ('User & Attachments', {'fields': ('user', 'content_type', 'object_id')}),
        ('File', {'fields': ('file', 'preview', 'file_name', 'file_size', 'mime_type', 'file_type')}),
        ('Image Details', {'fields': ('width', 'height', 'thumbnail')}),
        ('Access', {'fields': ('is_public', 'expires_at', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def file_size_display(self, obj):
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024*1024):.1f} MB"
    file_size_display.short_description = "Size"

    def preview(self, obj):
        if obj.file_type == 'image' and obj.file:
            return format_html(
                '<img src="{}" width="80" style="object-fit:cover; border-radius:4px;" />',
                obj.url
            )
        return "-"
    preview.short_description = "Preview"

from django.contrib import admin
from .models import AppSetting


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_preview', 'data_type', 'group', 'is_public', 'is_editable')
    list_filter = ('group', 'data_type', 'is_public', 'is_editable', 'is_required')
    search_fields = ('key', 'value', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('group', 'key')

    fieldsets = (
        ('Key & Type', {'fields': ('key', 'data_type', 'group')}),
        ('Value', {'fields': ('value', 'is_required')}),
        ('Settings', {'fields': ('is_public', 'is_editable', 'options')}),
        ('Description', {'fields': ('description',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def value_preview(self, obj):
        return obj.value[:50] + ('...' if len(obj.value) > 50 else '')
    value_preview.short_description = 'Value'

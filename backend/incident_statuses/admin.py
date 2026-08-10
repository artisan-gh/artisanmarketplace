from django.contrib import admin
from .models import IncidentStatus

@admin.register(IncidentStatus)
class IncidentStatusAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'ordering', 'is_active', 'is_terminal', 'color_code']
    list_filter = ['is_active', 'is_terminal']
    search_fields = ['name', 'description', 'code']
    ordering = ['ordering', 'name']
    readonly_fields = ['code']
    fields = ['code', 'name', 'description', 'is_active', 'ordering', 'color_code', 'is_terminal']

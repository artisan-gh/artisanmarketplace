from django.contrib import admin
from .models import IncidentPriority

@admin.register(IncidentPriority)
class IncidentPriorityAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'ordering', 'is_active', 'resolution_hours', 'color_code', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description', 'code']
    ordering = ['ordering', 'name']
    readonly_fields = ['code']
    fields = ['code', 'name', 'description', 'is_active', 'ordering', 'resolution_hours', 'escalation_hours', 'color_code']

from django.contrib import admin
from .models import Assignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['incident', 'artisan', 'status', 'assigned_at', 'accepted_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['incident__incident_number', 'artisan__email']
    raw_id_fields = ['incident', 'artisan', 'assigned_by']
    readonly_fields = ['assigned_at', 'accepted_at', 'started_at', 'completed_at']

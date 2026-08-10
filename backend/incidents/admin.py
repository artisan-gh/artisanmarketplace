from django.contrib import admin
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['incident_number', 'title', 'customer', 'priority', 'status', 'assigned_to', 'created_at']
    list_filter = ['priority', 'status', 'created_at']
    search_fields = ['incident_number', 'title', 'description', 'customer__name']
    readonly_fields = ['incident_number', 'created_at', 'updated_at', 'resolved_at', 'closed_at']
    fields = [
        'incident_number', 'customer', 'category', 'priority', 'status',
        'title', 'description', 'resolution_notes',
        'created_by', 'assigned_to', 'supervisor',
        'target_resolution', 'resolved_at', 'closed_at',
        'location_lat', 'location_lng', 'address',
        'created_at', 'updated_at'
    ]
    raw_id_fields = ['customer', 'created_by', 'assigned_to', 'supervisor']

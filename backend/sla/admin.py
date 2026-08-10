from django.contrib import admin
from .models import SLAPolicy, SLATracker


@admin.register(SLAPolicy)
class SLAPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'resolution_hours', 'is_active']
    list_filter = ['is_active', 'priority']
    search_fields = ['name', 'description']


@admin.register(SLATracker)
class SLATrackerAdmin(admin.ModelAdmin):
    list_display = ['incident', 'status', 'target_resolution', 'created_at']
    list_filter = ['status']
    search_fields = ['incident__incident_number']

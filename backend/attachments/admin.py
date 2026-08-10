from django.contrib import admin
from .models import Attachment

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'incident', 'filename', 'uploaded_by', 'created_at']
    search_fields = ['filename', 'incident__incident_number']
    readonly_fields = ['created_at']

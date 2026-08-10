from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'incident', 'user', 'created_at', 'is_internal']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['text', 'incident__incident_number']

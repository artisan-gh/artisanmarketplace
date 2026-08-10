from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'notification_type', 'is_read', 'sent_at']
    list_filter = ['is_read', 'notification_type', 'channel']
    search_fields = ['subject', 'message', 'user__email']
    raw_id_fields = ['user', 'incident', 'assignment']

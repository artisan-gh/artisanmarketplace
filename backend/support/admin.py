from django.contrib import admin
from .models import SupportTicket, SupportReply


class SupportReplyInline(admin.TabularInline):
    model = SupportReply
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('responder', 'message', 'is_internal', 'attachment', 'created_at')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'subject', 'user', 'assigned_to', 'status',
        'priority', 'category', 'reply_count', 'created_at'
    )
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('subject', 'message', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'resolved_at', 'closed_at')
    inlines = [SupportReplyInline]
    ordering = ('-created_at',)

    fieldsets = (
        ('User', {'fields': ('user', 'assigned_to')}),
        ('Details', {'fields': ('subject', 'message', 'category', 'priority')}),
        ('Status', {'fields': ('status', 'resolved_at', 'closed_at')}),
        ('Metadata', {'fields': ('is_public', 'attachment')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def reply_count(self, obj):
        return obj.replies.count()
    reply_count.short_description = 'Replies'


@admin.register(SupportReply)
class SupportReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'responder', 'message_preview', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('message', 'responder__email', 'ticket__subject')
    readonly_fields = ('created_at',)

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'

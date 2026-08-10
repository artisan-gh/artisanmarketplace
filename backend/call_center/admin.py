from django.contrib import admin
from .models import CallLog


@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = (
        'reference', 'agent', 'customer', 'direction',
        'caller_number', 'started_at', 'duration_seconds',
        'status', 'disposition', 'follow_up_required',
        'created_at'
    )
    list_filter = (
        'direction', 'channel', 'status', 'disposition',
        'follow_up_required', 'started_at'
    )
    search_fields = (
        'reference', 'caller_number', 'notes',
        'customer__name', 'agent__email'
    )
    readonly_fields = ('reference', 'duration_seconds', 'created_at', 'updated_at')
    raw_id_fields = ('agent', 'customer', 'incident')
    ordering = ('-started_at',)

    fieldsets = (
        ('Call Information', {
            'fields': ('reference', 'agent', 'customer', 'incident')
        }),
        ('Communication Details', {
            'fields': ('direction', 'channel', 'caller_number')
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at', 'duration_seconds')
        }),
        ('Status & Outcome', {
            'fields': ('status', 'disposition', 'notes', 'rating')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('status',)
        return self.readonly_fields

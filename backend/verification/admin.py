from django.contrib import admin
from django.utils.html import format_html
from .models import VerificationDocumentType, VerificationRequest


@admin.register(VerificationDocumentType)
class VerificationDocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'required_for_artisan')
    list_filter = ('is_active', 'required_for_artisan')
    search_fields = ('name', 'code', 'description')


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'document_type', 'document_preview', 'status',
        'created_at', 'approved_at'
    )
    list_filter = ('status', 'document_type', 'created_at')
    search_fields = ('user__email', 'document_number', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'approved_at', 'rejected_at', 'reviewed_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('User', {'fields': ('user', 'reviewed_by')}),
        ('Document', {'fields': ('document_type', 'document', 'document_back', 'document_number')}),
        ('Status', {'fields': ('status', 'approved_at', 'rejected_at', 'reviewed_at', 'expires_at')}),
        ('Notes', {'fields': ('notes', 'rejection_reason', 'admin_notes')}),
        ('Metadata', {'fields': ('ip_address', 'user_agent')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def document_preview(self, obj):
        if obj.document:
            return format_html(
                '<a href="{}" target="_blank">View Document</a>',
                obj.document.url
            )
        return "-"
    document_preview.short_description = "Document"

    actions = ['approve_selected', 'reject_selected']

    def approve_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            if obj.status in [VerificationRequest.Status.PENDING, VerificationRequest.Status.REVIEWING]:
                obj.approve(request.user)
                count += 1
        self.message_user(request, f"{count} verification requests approved.")
    approve_selected.short_description = "Approve selected"

    def reject_selected(self, request, queryset):
        count = 0
        for obj in queryset:
            if obj.status in [VerificationRequest.Status.PENDING, VerificationRequest.Status.REVIEWING]:
                obj.reject("Rejected via admin", request.user)
                count += 1
        self.message_user(request, f"{count} verification requests rejected.")
    reject_selected.short_description = "Reject selected"

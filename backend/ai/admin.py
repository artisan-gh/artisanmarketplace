from django.contrib import admin
from .models import AIModel, AIRequest


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'provider', 'model_type', 'is_active', 'is_default', 'total_requests')
    list_filter = ('is_active', 'is_default', 'provider', 'model_type')
    search_fields = ('name', 'description', 'model_id')
    readonly_fields = ('total_requests', 'total_successful', 'total_failed', 'created_at', 'updated_at')
    ordering = ('-is_active', 'name')

    fieldsets = (
        ('Model Info', {'fields': ('name', 'version', 'description', 'provider', 'model_type', 'model_id')}),
        ('Configuration', {'fields': ('config', 'max_tokens', 'cost_per_1k_tokens')}),
        ('Status', {'fields': ('is_active', 'is_default')}),
        ('Usage', {'fields': ('total_requests', 'total_successful', 'total_failed')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'model', 'request_type', 'status', 'tokens_used', 'latency_ms', 'created_at')
    list_filter = ('status', 'request_type', 'created_at')
    search_fields = ('request_id', 'error_message', 'input_data')
    readonly_fields = ('request_id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Request', {'fields': ('request_id', 'user', 'model', 'request_type')}),
        ('Data', {'fields': ('input_data', 'output_data', 'metadata')}),
        ('Performance', {'fields': ('tokens_used', 'tokens_prompt', 'tokens_completion', 'latency_ms', 'cost')}),
        ('Status', {'fields': ('status', 'error_message', 'error_code', 'started_at', 'completed_at')}),
        ('Metadata', {'fields': ('ip_address', 'created_at', 'updated_at')}),
    )

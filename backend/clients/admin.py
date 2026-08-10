from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'company_name',
        'preferred_location',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company_name', 'preferred_location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Profile', {'fields': ('company_name', 'preferred_location')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

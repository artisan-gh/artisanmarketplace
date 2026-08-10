from django.contrib import admin
from .models import SystemSetting, ApplicationLog


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):

    list_display = (
        "key",
        "value",
        "created_at"
    )


@admin.register(ApplicationLog)
class ApplicationLogAdmin(admin.ModelAdmin):

    list_display = (
        "level",
        "created_at"
    )

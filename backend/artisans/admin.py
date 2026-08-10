from django.contrib import admin
from .models import ArtisanProfile, Skill, ArtisanAvailability


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name', 'description']


@admin.register(ArtisanProfile)
class ArtisanProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'category', 'is_available',
        'average_rating', 'max_concurrent_jobs', 'current_workload'
    ]
    list_filter = ['is_available', 'category']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    raw_id_fields = ['user', 'category']
    filter_horizontal = ['skills', 'legacy_skills']   # both new and old skills

    fieldsets = (
        (None, {
            'fields': ('user', 'category', 'is_available')
        }),
        ('Skills', {
            'fields': ('skills', 'legacy_skills')
        }),
        ('Location & Work', {
            'fields': ('current_location_lat', 'current_location_lng', 'max_concurrent_jobs')
        }),
        ('Profile', {
            'fields': ('average_rating', 'hire_date', 'bio')
        }),
    )

    def current_workload(self, obj):
        return obj.current_workload
    current_workload.short_description = 'Current Workload'


@admin.register(ArtisanAvailability)
class ArtisanAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['artisan', 'get_day_display', 'start_time', 'end_time', 'is_working']
    list_filter = ['day_of_week', 'is_working']
    ordering = ['artisan', 'day_of_week']

    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Day'

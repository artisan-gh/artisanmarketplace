from django.contrib import admin
from .models import JobCategory, Job, JobApplication, SavedJob


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'location', 'status', 'applications_count', 'created_at')
    list_filter = ('status', 'job_type', 'experience_level', 'is_remote')
    search_fields = ('title', 'description', 'company__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('posted_at', 'updated_at', 'views', 'applications_count')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'candidate', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'candidate__email')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'created_at')

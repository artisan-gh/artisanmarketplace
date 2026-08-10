from django.contrib import admin
from .models import (
    CourseCategory, Course, Lesson, Enrollment,
    LessonProgress, Quiz, Question, Choice, Certificate
)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'order', 'content_type', 'is_free_preview', 'duration_minutes')


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'level', 'is_published', 'is_featured')
    list_filter = ('level', 'is_published', 'is_featured', 'category')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'status', 'progress_percent', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__email', 'course__title')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'score')
    list_filter = ('is_completed',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'enrollment', 'issued_at')

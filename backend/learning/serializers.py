from rest_framework import serializers
from .models import (
    CourseCategory, Course, Lesson, Enrollment,
    LessonProgress, Quiz, Question, Choice, Certificate
)
from accounts.serializers import UserSerializer


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ('id', 'name', 'slug', 'description', 'icon', 'is_active')


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            'id', 'title', 'description', 'content_type', 'content_url',
            'content_text', 'attachment', 'order', 'duration_minutes',
            'is_free_preview', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')


class CourseSerializer(serializers.ModelSerializer):
    instructor_detail = UserSerializer(source='instructor', read_only=True)
    category_detail = CourseCategorySerializer(source='category', read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'instructor', 'instructor_detail', 'category', 'category_detail',
            'title', 'slug', 'description', 'objectives', 'level', 'price',
            'currency', 'image', 'promo_video', 'duration_hours', 'total_lessons',
            'is_published', 'is_featured', 'is_free', 'enrollments_count',
            'rating', 'reviews_count', 'lessons', 'lessons_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('slug', 'enrollments_count', 'rating', 'reviews_count', 'created_at', 'updated_at')


class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'slug', 'image', 'price', 'currency', 'level',
            'duration_hours', 'total_lessons', 'is_published', 'is_free',
            'rating', 'enrollments_count', 'instructor_name', 'category_name'
        )


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'category', 'title', 'description', 'objectives', 'level',
            'price', 'currency', 'image', 'promo_video', 'duration_hours',
            'is_published', 'is_featured', 'is_free'
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    student_detail = UserSerializer(source='student', read_only=True)
    course_detail = CourseListSerializer(source='course', read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            'id', 'course', 'course_detail', 'student', 'student_detail',
            'status', 'progress_percent', 'completed_at', 'payment', 'created_at'
        )
        read_only_fields = ('student', 'progress_percent', 'completed_at', 'created_at')


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_detail = LessonSerializer(source='lesson', read_only=True)

    class Meta:
        model = LessonProgress
        fields = ('id', 'enrollment', 'lesson', 'lesson_detail', 'is_completed', 'score', 'last_accessed')
        read_only_fields = ('enrollment', 'last_accessed')


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'choice_text', 'is_correct')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'order', 'choices')


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'pass_score', 'questions')


class CertificateSerializer(serializers.ModelSerializer):
    enrollment_detail = EnrollmentSerializer(source='enrollment', read_only=True)

    class Meta:
        model = Certificate
        fields = ('id', 'enrollment', 'enrollment_detail', 'certificate_number', 'issued_at', 'file')
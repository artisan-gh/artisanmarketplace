from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import models
from .models import (
    CourseCategory, Course, Lesson, Enrollment,
    LessonProgress, Quiz, Question, Choice, Certificate
)
from .serializers import (
    CourseCategorySerializer, CourseSerializer, CourseListSerializer,
    CourseCreateSerializer, LessonSerializer, EnrollmentSerializer,
    LessonProgressSerializer, QuizSerializer, CertificateSerializer
)


class CourseCategoryViewSet(viewsets.ModelViewSet):
    queryset = CourseCategory.objects.filter(is_active=True).all()
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('instructor', 'category').prefetch_related('lessons').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'level', 'is_published', 'is_free', 'is_featured']
    search_fields = ['title', 'description', 'objectives']
    ordering_fields = ['price', 'rating', 'enrollments_count', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(is_published=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        if self.action == 'create':
            return CourseCreateSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        course = self.get_object()
        if not course.is_published:
            return Response({'error': 'Course is not published.'}, status=status.HTTP_400_BAD_REQUEST)
        enrollment, created = Enrollment.objects.get_or_create(
            course=course,
            student=request.user
        )
        if created:
            course.enrollments_count += 1
            course.save()
            return Response({'status': 'enrolled'})
        return Response({'status': 'already_enrolled'})

    @action(detail=True, methods=['post'])
    def unenroll(self, request, pk=None):
        course = self.get_object()
        enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
        if enrollment:
            enrollment.delete()
            course.enrollments_count = max(0, course.enrollments_count - 1)
            course.save()
            return Response({'status': 'unenrolled'})
        return Response({'error': 'Not enrolled.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('course').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course']
    ordering_fields = ['order']

    def get_serializer_class(self):
        return LessonSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('course', 'student').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'status']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return self.queryset.filter(student=self.request.user)

    def get_serializer_class(self):
        return EnrollmentSerializer

    @action(detail=True, methods=['post'])
    def complete_lesson(self, request, pk=None):
        enrollment = self.get_object()
        lesson_id = request.data.get('lesson_id')
        if not lesson_id:
            return Response({'error': 'lesson_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        lesson = get_object_or_404(Lesson, id=lesson_id, course=enrollment.course)
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            # Update enrollment progress
            total_lessons = enrollment.course.lessons.count()
            completed = LessonProgress.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).count()
            enrollment.progress_percent = int((completed / total_lessons) * 100) if total_lessons else 0
            if enrollment.progress_percent == 100:
                enrollment.status = Enrollment.Status.COMPLETED
                enrollment.completed_at = timezone.now()
                # Generate certificate
                Certificate.objects.get_or_create(enrollment=enrollment)
            enrollment.save()
        return Response({'status': 'lesson_completed'})


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related('lesson').all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        answers = request.data.get('answers', {})  # {question_id: choice_id}
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=quiz.lesson.course
        ).first()
        if not enrollment:
            return Response({'error': 'You must be enrolled.'}, status=status.HTTP_403_FORBIDDEN)
        # Calculate score
        correct = 0
        total = quiz.questions.count()
        for question in quiz.questions.all():
            selected = answers.get(str(question.id))
            if selected:
                choice = question.choices.filter(id=selected, is_correct=True).first()
                if choice:
                    correct += 1
        score = (correct / total) * 100 if total else 0
        # Update progress
        progress = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=quiz.lesson
        )[0]
        progress.score = score
        if score >= quiz.pass_score:
            progress.is_completed = True
            progress.completed_at = timezone.now()
        progress.save()
        return Response({'score': score, 'passed': score >= quiz.pass_score})

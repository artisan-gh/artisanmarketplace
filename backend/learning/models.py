from django.db import models
from django.conf import settings
from django.utils.text import slugify
from common.models import TimeStampedModel


class CourseCategory(TimeStampedModel):
    """
    Category for organising courses.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Course Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(TimeStampedModel):
    """
    A course with lessons and learning materials.
    """
    class Level(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught'
    )

    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )

    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    objectives = models.TextField(blank=True, help_text="What students will learn")

    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='GHS')

    # Media
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    promo_video = models.URLField(blank=True, help_text="YouTube/Vimeo URL")

    # Duration
    duration_hours = models.PositiveIntegerField(default=1)
    total_lessons = models.PositiveIntegerField(default=0)

    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)

    # Engagement
    enrollments_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instructor', 'is_published']),
            models.Index(fields=['category']),
            models.Index(fields=['level']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Lesson(TimeStampedModel):
    """
    A lesson within a course.
    """
    class ContentType(models.TextChoices):
        VIDEO = 'VIDEO', 'Video'
        TEXT = 'TEXT', 'Text'
        PDF = 'PDF', 'PDF'
        QUIZ = 'QUIZ', 'Quiz'
        ASSIGNMENT = 'ASSIGNMENT', 'Assignment'

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    content_type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.VIDEO)
    content_url = models.URLField(blank=True, help_text="URL for video or external content")
    content_text = models.TextField(blank=True, help_text="Text content")
    attachment = models.FileField(upload_to='lessons/', blank=True, null=True)

    order = models.PositiveIntegerField(default=0, help_text="Lesson order in the course")
    duration_minutes = models.PositiveIntegerField(default=0)

    is_free_preview = models.BooleanField(default=False, help_text="Can be viewed without enrollment")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.course.title})"


class Enrollment(TimeStampedModel):
    """
    Student enrollment in a course with progress tracking.
    """
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        DROPPED = 'DROPPED', 'Dropped'

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrolled_courses'
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    progress_percent = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Payment info (optional)
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='course_enrollments'
    )

    class Meta:
        unique_together = ['course', 'student']

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"


class LessonProgress(TimeStampedModel):
    """
    Progress for each lesson within an enrollment.
    """
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )

    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    # For quizzes/assignments
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        return f"{self.enrollment.student.email} - {self.lesson.title}"


class Quiz(TimeStampedModel):
    """
    Quiz/assessment for a lesson.
    """
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    title = models.CharField(max_length=200)
    pass_score = models.PositiveIntegerField(default=70, help_text="Percentage required to pass")

    def __str__(self):
        return f"Quiz for {self.lesson.title}"


class Question(TimeStampedModel):
    """
    A question in a quiz.
    """
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question_text[:50]


class Choice(TimeStampedModel):
    """
    A choice/answer option for a question.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Certificate(TimeStampedModel):
    """
    Certificate awarded to a student upon course completion.
    """
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='certificate'
    )
    certificate_number = models.CharField(max_length=50, unique=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import uuid
            self.certificate_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate for {self.enrollment.student.email}"

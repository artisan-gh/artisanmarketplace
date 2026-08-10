from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'learning'

router = DefaultRouter()
router.register(r'categories', views.CourseCategoryViewSet, basename='course-category')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'lessons', views.LessonViewSet, basename='lesson')
router.register(r'enrollments', views.EnrollmentViewSet, basename='enrollment')
router.register(r'quizzes', views.QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
]
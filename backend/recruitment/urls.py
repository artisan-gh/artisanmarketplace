from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'recruitment'

router = DefaultRouter()
router.register(r'categories', views.JobCategoryViewSet, basename='job-category')
router.register(r'jobs', views.JobViewSet, basename='job')
router.register(r'applications', views.JobApplicationViewSet, basename='job-application')
router.register(r'saved', views.SavedJobViewSet, basename='saved-job')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArtisanProfileViewSet, SkillViewSet

app_name = 'artisans'
router = DefaultRouter()
router.register(r'profiles', ArtisanProfileViewSet, basename='artisanprofile')
router.register(r'skills', SkillViewSet, basename='skill')

urlpatterns = [
    path('', include(router.urls)),
]
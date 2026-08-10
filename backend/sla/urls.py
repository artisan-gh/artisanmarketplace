from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SLAPolicyViewSet, SLATrackerViewSet

app_name = 'sla'
router = DefaultRouter()
router.register(r'policies', SLAPolicyViewSet, basename='sla-policy')
router.register(r'trackers', SLATrackerViewSet, basename='sla-tracker')

urlpatterns = [
    path('', include(router.urls)),
]
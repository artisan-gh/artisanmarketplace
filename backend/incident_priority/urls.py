from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidentPriorityViewSet

app_name = 'incident_priority'
router = DefaultRouter()
router.register(r'', IncidentPriorityViewSet, basename='incidentpriority')

urlpatterns = [
    path('', include(router.urls)),
]
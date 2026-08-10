from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidentStatusViewSet

app_name = 'incident_statuses'
router = DefaultRouter()
router.register(r'', IncidentStatusViewSet, basename='incidentstatus')

urlpatterns = [
    path('', include(router.urls)),
]
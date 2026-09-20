from rest_framework.routers import DefaultRouter

from .views_client import IncidentClientViewSet

app_name = "incidents_client"

router = DefaultRouter()
router.register(r"", IncidentClientViewSet, basename="client-incident")

urlpatterns = router.urls
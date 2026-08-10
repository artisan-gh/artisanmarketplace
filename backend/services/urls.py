from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ServiceViewSet

app_name = "services"

router = DefaultRouter()

# Services
router.register(
    r"",
    ServiceViewSet,
    basename="service"
)

urlpatterns = [
    path("", include(router.urls)),
]
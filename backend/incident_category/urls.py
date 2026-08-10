from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import IncidentCategoryViewSet, SubCategoryViewSet

router = DefaultRouter()

# Register this FIRST
router.register(r"subcategories", SubCategoryViewSet, basename="subcategory")

# Register this SECOND
router.register(r"", IncidentCategoryViewSet, basename="incidentcategory")

urlpatterns = [
    path("", include(router.urls)),
]
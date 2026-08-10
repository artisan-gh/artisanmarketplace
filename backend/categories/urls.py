from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    SubCategoryViewSet,
)

app_name = "categories"

router = DefaultRouter()

# Categories
router.register(
    r"",
    CategoryViewSet,
    basename="category"
)

# SubCategories
router.register(
    r"subcategories",
    SubCategoryViewSet,
    basename="subcategory"
)

urlpatterns = [
    path("", include(router.urls)),
]
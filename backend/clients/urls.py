from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet

app_name = 'clients'

router = DefaultRouter()
router.register(r'', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
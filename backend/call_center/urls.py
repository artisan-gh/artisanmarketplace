from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CallLogViewSet

app_name = 'call_center'
router = DefaultRouter()
router.register(r'call-logs', CallLogViewSet, basename='call-log')

urlpatterns = [
    path('', include(router.urls)),
]
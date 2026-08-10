from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttachmentViewSet

app_name = 'attachments'
router = DefaultRouter()
router.register(r'', AttachmentViewSet, basename='attachment')

urlpatterns = [
    path('', include(router.urls)),
]
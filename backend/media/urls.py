from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'media'

router = DefaultRouter()
router.register(r'', views.MediaFileViewSet, basename='media')

urlpatterns = [
    path('', include(router.urls)),
]
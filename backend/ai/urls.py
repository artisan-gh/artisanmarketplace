from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'ai'

router = DefaultRouter()
router.register(r'models', views.AIModelViewSet, basename='ai-model')
router.register(r'requests', views.AIRequestViewSet, basename='ai-request')

urlpatterns = [
    path('', include(router.urls)),
]
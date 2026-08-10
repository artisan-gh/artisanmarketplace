from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'app_settings'

router = DefaultRouter()
router.register(r'', views.AppSettingViewSet, basename='app-setting')

urlpatterns = [
    path('', include(router.urls)),
]
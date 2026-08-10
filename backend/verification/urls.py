from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'verification'

router = DefaultRouter()
router.register(r'document-types', views.VerificationDocumentTypeViewSet, basename='verification-document-type')
router.register(r'', views.VerificationRequestViewSet, basename='verification')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import SupportTicketViewSet

app_name = 'support'

router = DefaultRouter()
router.register(r'tickets', SupportTicketViewSet, basename='support-ticket')

urlpatterns = [
    path('', include(router.urls)),
]
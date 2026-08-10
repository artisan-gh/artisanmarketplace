from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import SubscriptionPlanViewSet, SubscriptionViewSet

app_name = 'subscriptions'

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]
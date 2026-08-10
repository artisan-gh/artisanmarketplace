from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView  # <-- added import

from .views import (
    UserViewSet,
    SessionViewSet,
    LoginHistoryViewSet,
    CustomTokenObtainPairView,
    LogoutView,
    RegisterView,
)

app_name = "accounts"

# Router for ViewSets
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"sessions", SessionViewSet, basename="session")
router.register(r"login-history", LoginHistoryViewSet, basename="login-history")

urlpatterns = [
    # Public endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # <-- added

    # Authentication (requires valid token)
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # Include all router URLs
    path("", include(router.urls)),
]
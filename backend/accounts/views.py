# accounts/views.py

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
import json

from .models import User, LoginHistory, UserSession
from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserStatusUpdateSerializer,
    ChangePasswordSerializer,
    LoginHistorySerializer,
    UserSessionSerializer,
    CustomTokenObtainPairSerializer,
    UserRegisterSerializer,
)

# ─── Import artisan models ──────────────────────────────────
from artisans.models import ArtisanProfile, ArtisanAvailability


# ------------------------------------------------------------
# 1. CUSTOM JWT LOGIN VIEW
# ------------------------------------------------------------
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ------------------------------------------------------------
# 2. PUBLIC REGISTRATION VIEW (with duplicate protection)
# ------------------------------------------------------------
class RegisterView(APIView):
    """
    Public registration endpoint.
    Creates a user with account_status=PENDING and is_active=False.
    Admin must approve the account.
    If user_type = 'ARTISAN', also creates/updates ArtisanProfile with
    category, skills, and availability.
    Supports multipart/form-data for file uploads.
    """
    permission_classes = []  # Public
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            # ─── Handle artisan profile (create or update) ──
            if request.data.get('user_type') == 'ARTISAN':
                category_id = request.data.get('category')
                skills_data = request.data.get('skills')
                availability_data = request.data.get('availability_days')

                # ✅ Use get_or_create to avoid duplicate constraint
                artisan_profile, created = ArtisanProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'category_id': category_id if category_id else None,
                        'is_available': True,
                    }
                )

                # If profile already existed, update category if provided
                if not created and category_id:
                    artisan_profile.category_id = category_id
                    artisan_profile.is_available = True
                    artisan_profile.save(update_fields=['category_id', 'is_available'])

                # ─── Add skills (list of IDs) ──────────────
                if skills_data:
                    try:
                        skills_list = json.loads(skills_data) if isinstance(skills_data, str) else skills_data
                        if skills_list:
                            artisan_profile.skills.set(skills_list)
                    except (json.JSONDecodeError, TypeError):
                        pass

                # ─── Add availability days ─────────────────────
                if availability_data:
                    try:
                        days = json.loads(availability_data) if isinstance(availability_data, str) else availability_data
                        day_map = {
                            'MONDAY': 0, 'TUESDAY': 1, 'WEDNESDAY': 2,
                            'THURSDAY': 3, 'FRIDAY': 4, 'SATURDAY': 5, 'SUNDAY': 6
                        }
                        # Clear existing availability and re‑create to avoid duplicates
                        artisan_profile.availability.all().delete()
                        for day_str in days:
                            if day_str in day_map:
                                ArtisanAvailability.objects.create(
                                    artisan=artisan_profile,
                                    day_of_week=day_map[day_str],
                                    start_time='08:00:00',
                                    end_time='17:00:00',
                                    is_working=True
                                )
                    except (json.JSONDecodeError, TypeError, KeyError):
                        pass

            # Optional: send welcome email or admin notification
            return Response(
                {
                    "message": "Registration successful. Your account is pending admin approval.",
                    "user": UserDetailSerializer(user, context={"request": request}).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------
# 3. LOGOUT VIEW
# ------------------------------------------------------------
class LogoutView(APIView):
    """
    Logout endpoint: revokes the refresh token, marks user offline.
    Expects a refresh token in the request body.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"refresh": "This field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            jti = token.get("jti")
            session = UserSession.objects.filter(jti=jti, user=request.user).first()
            if session and not session.revoked:
                session.revoke()

            user = request.user
            user.is_online = False
            user.last_seen = timezone.now()
            user.save(update_fields=["is_online", "last_seen"])

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

        except TokenError as e:
            raise InvalidToken(str(e))
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------
# 4. USER VIEWSET (CRUD + custom actions)
# ------------------------------------------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        if self.action == "status_update":
            return UserStatusUpdateSerializer
        return UserDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return User.objects.filter(is_deleted=False)
        if user.is_manager and user.department:
            return User.objects.filter(department=user.department, is_deleted=False)
        return User.objects.filter(id=user.id, is_deleted=False)

    def get_permissions(self):
        if self.action in ["create", "destroy", "status_update"]:
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.hard_delete()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = UserDetailSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        update_session_auth_hash(request, user)

        return Response({"message": "Password updated successfully."})

    @action(detail=True, methods=["patch"], url_path="status")
    def status_update(self, request, pk=None):
        user = self.get_object()
        serializer = UserStatusUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ------------------------------------------------------------
# 5. SESSION VIEWSET
# ------------------------------------------------------------
class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user, revoked=False)

    @action(detail=False, methods=["post"], url_path="revoke-all")
    def revoke_all(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"refresh": "This field is required to keep the current session."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            current_jti = token.get("jti")
        except TokenError:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        sessions = UserSession.objects.filter(user=request.user, revoked=False).exclude(jti=current_jti)
        count = sessions.count()
        for session in sessions:
            session.revoke()

        return Response(
            {"message": f"Revoked {count} other sessions. Current session remains active."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="revoke")
    def revoke(self, request, pk=None):
        session = self.get_object()
        if session.user != request.user:
            return Response(
                {"error": "You can only revoke your own sessions."},
                status=status.HTTP_403_FORBIDDEN,
            )
        session.revoke()
        return Response({"message": "Session revoked successfully."})


# ------------------------------------------------------------
# 6. LOGIN HISTORY VIEWSET
# ------------------------------------------------------------
class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return LoginHistory.objects.all()
        if user.is_manager and user.department:
            dept_users = User.objects.filter(department=user.department).values_list("id", flat=True)
            return LoginHistory.objects.filter(user_id__in=dept_users)
        return LoginHistory.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

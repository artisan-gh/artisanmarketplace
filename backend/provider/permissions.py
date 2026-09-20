
from rest_framework import permissions


PROVIDER_USER_TYPES = {"ARTISAN", "PROVIDER", "AGENT"}


def _user_type(user) -> str:
    return (getattr(user, "user_type", "") or "").upper()


class IsProvider(permissions.BasePermission):
    message = "Only service providers can access the Test Centre."

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and _user_type(u) in PROVIDER_USER_TYPES)


class IsAttemptOwner(permissions.BasePermission):
    message = "You do not have access to this attempt."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsSupportStaff(permissions.BasePermission):
    message = "Only support staff can reset attempts."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

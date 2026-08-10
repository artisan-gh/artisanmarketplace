from rest_framework import permissions
from .models import User


class IsAdminOrStaff(permissions.BasePermission):
    """
    Allows access only to admin or staff users (Django's is_staff/is_superuser).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        )


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to ADMIN user_type.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type == User.UserType.ADMIN
        )


class IsAgent(permissions.BasePermission):
    """
    Allows access only to AGENT or ADMIN user_type.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type in (User.UserType.AGENT, User.UserType.ADMIN)
        )


class IsArtisan(permissions.BasePermission):
    """
    Allows access only to ARTISAN or ADMIN user_type.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type in (User.UserType.ARTISAN, User.UserType.ADMIN)
        )


class IsDispatcher(permissions.BasePermission):
    """
    Allows access only to DISPATCHER or ADMIN user_type.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type in (User.UserType.DISPATCHER, User.UserType.ADMIN)
        )


class IsSupervisor(permissions.BasePermission):
    """
    Allows access only to SUPERVISOR or ADMIN user_type.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type in (User.UserType.SUPERVISOR, User.UserType.ADMIN)
        )


class IsManager(permissions.BasePermission):
    """
    Allows access only to MANAGER or ADMIN user_type.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type in (User.UserType.MANAGER, User.UserType.ADMIN)
        )


class IsCompany(permissions.BasePermission):
    """
    Allows access only to COMPANY or ADMIN user_type.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type in (User.UserType.COMPANY, User.UserType.ADMIN)
        )
from rest_framework.permissions import BasePermission


class CanViewAuditLogs(BasePermission):
    """
    Allow only staff or users with specific permission to view audit logs.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or
            request.user.has_perm("audit.view_auditlog")
        )
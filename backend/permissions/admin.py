from django.contrib import admin
from .models import Role, Permission, RolePermission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "created_at"
    )



@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "codename"
    )



@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):

    list_display = (
        "role",
        "permission"
    )

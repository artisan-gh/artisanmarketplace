from django.db import models


class Role(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.name



class Permission(models.Model):

    name = models.CharField(
        max_length=100
    )

    codename = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )


    def __str__(self):
        return self.name



class RolePermission(models.Model):

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE
    )


    class Meta:
        unique_together = (
            "role",
            "permission"
        )


    def __str__(self):
        return f"{self.role} - {self.permission}"

from django.db import models


class SystemSetting(models.Model):

    key = models.CharField(
        max_length=100,
        unique=True
    )

    value = models.TextField()

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):
        return self.key



class ApplicationLog(models.Model):

    level = models.CharField(
        max_length=50
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.level

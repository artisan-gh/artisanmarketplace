from django.db import models
from django.conf import settings
from common.models import TimeStampedModel


class Client(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile"
    )

    company_name = models.CharField(
        max_length=150,
        blank=True
    )

    preferred_location = models.CharField(
        max_length=150,
        blank=True
    )

    def __str__(self):
        return self.user.email

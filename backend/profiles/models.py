from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    profile_completed = models.BooleanField(
        default=False
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    occupation = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.email} Profile"


class Address(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    address_type = models.CharField(
        max_length=50,
        default="Home"
    )

    street = models.CharField(
        max_length=255
    )

    city = models.CharField(
        max_length=100
    )

    region = models.CharField(
        max_length=100
    )

    country = models.CharField(
        max_length=100,
        default="Ghana"
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    is_default = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return f"{self.city}, {self.region}"


class EmergencyContact(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emergency_contacts"
    )

    name = models.CharField(
        max_length=100
    )

    relationship = models.CharField(
        max_length=50
    )

    phone = models.CharField(
        max_length=20
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.name

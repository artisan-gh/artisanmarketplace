from django.contrib import admin
from .models import Profile, Address, EmergencyContact


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "occupation",
        "profile_completed",
        "created_at"
    )

    search_fields = (
        "user__email",
        "occupation"
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "city",
        "region",
        "country",
        "is_default"
    )

    search_fields = (
        "city",
        "region",
        "user__email"
    )


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "name",
        "relationship",
        "phone"
    )

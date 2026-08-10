from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from accounts.models import (
    AgentProfile,
    SupervisorProfile,
    DispatcherProfile,
    ManagerProfile,
    CompanyProfile,
    AdminProfile,
)
from artisans.models import ArtisanProfile
from clients.models import Client
from wallets.models import Wallet

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create profiles and related records when a new User is created.

    User Types:
    - ARTISAN
    - AGENT
    - SUPERVISOR
    - DISPATCHER
    - MANAGER
    - COMPANY
    - ADMIN

    Every user automatically receives a Wallet.
    """

    if not created:
        return

    # =========================================================================
    # Create Wallet for Every User
    # =========================================================================
    Wallet.objects.get_or_create(user=instance)

    # =========================================================================
    # ARTISAN
    # =========================================================================
    if instance.user_type == "ARTISAN":
        ArtisanProfile.objects.get_or_create(
            user=instance,
            defaults={
                "bio": "",
                "is_available": True,
                "max_concurrent_jobs": 3,
                "average_rating": 0.0,
                "hire_date": None,
            },
        )

    # =========================================================================
    # AGENT
    # =========================================================================
    elif instance.user_type == "AGENT":
        AgentProfile.objects.get_or_create(
            user=instance,
            defaults={
                "extension": None,
                "assigned_queue": None,
                "is_active": True,
            },
        )

    # =========================================================================
    # SUPERVISOR
    # =========================================================================
    elif instance.user_type == "SUPERVISOR":
        SupervisorProfile.objects.get_or_create(
            user=instance,
            defaults={
                "team_size": 0,
                "is_active": True,
            },
        )

    # =========================================================================
    # DISPATCHER
    # =========================================================================
    elif instance.user_type == "DISPATCHER":
        DispatcherProfile.objects.get_or_create(
            user=instance,
            defaults={
                "is_active": True,
            },
        )

    # =========================================================================
    # MANAGER
    # =========================================================================
    elif instance.user_type == "MANAGER":
        ManagerProfile.objects.get_or_create(
            user=instance,
            defaults={
                "department": "",
                "is_active": True,
            },
        )

    # =========================================================================
    # COMPANY
    # =========================================================================
    elif instance.user_type == "COMPANY":
        CompanyProfile.objects.get_or_create(
            user=instance,
            defaults={
                "company_name": "",
                "is_active": True,
            },
        )

        # Company users are also clients
        Client.objects.get_or_create(user=instance)

    # =========================================================================
    # ADMIN
    # =========================================================================
    elif instance.user_type == "ADMIN":
        AdminProfile.objects.get_or_create(
            user=instance,
            defaults={
                "is_active": True,
            },
        )

    # =========================================================================
    # OTHER USER TYPES
    # =========================================================================
    else:
        # Wallet already created above.
        pass
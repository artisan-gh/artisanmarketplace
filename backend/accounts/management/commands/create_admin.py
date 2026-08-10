import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the admin superuser"

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get(
            "ADMIN_EMAIL",
            "artisanhub3g@gmail.com",
        )
        password = os.environ.get("ADMIN_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "ADMIN_PASSWORD environment variable is not set."
                )
            )
            return

        user = User.objects.filter(email=email).first()

        if user:
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user updated: {email}"
                )
            )
        else:
            User.objects.create_superuser(
                email=email,
                password=password,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user created: {email}"
                )
            )
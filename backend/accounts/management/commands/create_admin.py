from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Create or update the admin superuser"

    def handle(self, *args, **options):
        User = get_user_model()

        email = "artisanhub3g@gmail.com"
        password = "Dawudagood@2024"

        try:
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
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Admin user created: {email}"
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to create admin: {e}"
                )
            )
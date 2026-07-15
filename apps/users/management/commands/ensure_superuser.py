import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create the admin superuser from DJANGO_SUPERUSER_EMAIL / "
        "DJANGO_SUPERUSER_PASSWORD env vars, or reset its password/flags if "
        "it already exists. Safe to run on every deploy."
    )

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not email or not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD not set "
                "in the environment - skipping admin account setup."
            ))
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"is_staff": True, "is_superuser": True},
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Reset password/flags for"
        self.stdout.write(self.style.SUCCESS(f"{action} superuser {email!r}."))

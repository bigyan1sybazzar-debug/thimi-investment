from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Resets passwords for all non-admin members to 'thimi123'."

    def handle(self, *args, **options):
        non_admin_users = User.objects.filter(is_staff=False, is_superuser=False)
        count = 0
        for u in non_admin_users:
            u.set_password("thimi123")
            u.save()
            count += 1
            self.stdout.write(self.style.SUCCESS(f"Reset password for member: {u.username}"))

        self.stdout.write(
            self.style.SUCCESS(f"\nSuccessfully reset {count} member password(s) to 'thimi123'. Admin accounts were excluded.")
        )

from django.core.management.base import BaseCommand
from accounts.models import Member, User

MEMBER_EMAILS = {
    'M0001': 'atlanticbhandari@gmail.com',
    'M0002': 'bigyan.neupane6@gmail.com',
    'M0003': 'bkalpa.khadka@gmail.com',
    'M0004': 'bishalpandey32166@gmail.com',
    'M0005': 'sharmadevendra410@gmail.com',
    'M0006': 'dipin432@gmail.com',
    'M0007': 'nishhan.neupane@gmail.com',
    'M0008': 'mepaone3@gmail.com',
    'M0009': 'prabn0115@gmail.com',
    'M0010': 'Pradeeptandan40@gmail.com',
    'M0011': 'Prashantadhikari121@gmail.com',
    'M0012': 'adhikaripratik314@gmail.com',
    'M0013': 'sandeshupadhya1@gmail.com',
    'M0014': 'vs.raimajhi@gmail.com',
    'M0015': 'dahalyuben@gmail.com',
}


class Command(BaseCommand):
    help = 'Syncs member user emails with production database'

    def handle(self, *args, **options):
        updated_count = 0
        for member_id, email in MEMBER_EMAILS.items():
            try:
                member = Member.objects.select_related('user').get(member_id=member_id)
                user = member.user
                changed = False
                if user.email != email:
                    user.email = email
                    changed = True
                if user.username != email:
                    user.username = email
                    changed = True
                if changed:
                    user.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated {member_id} ({user.username}) email to {email}"))
            except Member.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Member {member_id} not found in database."))

        self.stdout.write(self.style.SUCCESS(f"Finished email sync. Updated {updated_count} member email(s)."))

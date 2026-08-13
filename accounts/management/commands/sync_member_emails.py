from django.core.management.base import BaseCommand
from accounts.models import Member, User

MEMBER_EMAILS = {
    'M0001': 'atlantic@thimi.com',
    'M0002': 'bigyan.neupane6@gmail.com',
    'M0003': 'bkalpa.khadka@gmail.com',
    'M0004': 'bishalpandey32166@gmail.com',
    'M0005': 'devendra@thimi.com',
    'M0006': 'dipin@thimi.com',
    'M0007': 'nishan@thimi.com',
    'M0008': 'mepaone3@gmail.com',
    'M0009': 'prabin@thimi.com',
    'M0010': 'Pradeeptandan40@gmail.com',
    'M0011': 'prashant@thimi.com',
    'M0012': 'pratik@thimi.com',
    'M0013': 'sandeshupadhya1@gmail.com',
    'M0014': 'vikram@thimi.com',
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
                if user.email != email:
                    user.email = email
                    user.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Updated {member_id} ({user.username}) email to {email}"))
            except Member.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Member {member_id} not found in database."))

        self.stdout.write(self.style.SUCCESS(f"Finished email sync. Updated {updated_count} member email(s)."))

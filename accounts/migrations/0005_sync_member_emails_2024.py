from django.db import migrations

MEMBER_EMAILS = {
    'M0001': ('atlanticbhandari@gmail.com', 'atlanticbhandari@gmail.com'),
    'M0002': ('bigyan.neupane6@gmail.com', 'bigyan.neupane6@gmail.com'),
    'M0003': ('bkalpa.khadka@gmail.com',  'bkalpa.khadka@gmail.com'),
    'M0004': ('bishalpandey32166@gmail.com', 'bishalpandey32166@gmail.com'),
    'M0005': ('sharmadevendra410@gmail.com', 'sharmadevendra410@gmail.com'),
    'M0006': ('dipin432@gmail.com',        'dipin432@gmail.com'),
    'M0007': ('nishhan.neupane@gmail.com',       'nishhan.neupane@gmail.com'),
    'M0008': ('mepaone3@gmail.com',     'mepaone3@gmail.com'),
    'M0009': ('prabn0115@gmail.com',       'prabn0115@gmail.com'),
    'M0010': ('Pradeeptandan40@gmail.com', 'Pradeeptandan40@gmail.com'),
    'M0011': ('Prashantadhikari121@gmail.com', 'Prashantadhikari121@gmail.com'),
    'M0012': ('adhikaripratik314@gmail.com', 'adhikaripratik314@gmail.com'),
    'M0013': ('sandeshupadhya1@gmail.com', 'sandeshupadhya1@gmail.com'),
    'M0014': ('vs.raimajhi@gmail.com',       'vs.raimajhi@gmail.com'),
    'M0015': ('dahalyuben@gmail.com',   'dahalyuben@gmail.com'),
}



def sync_emails(apps, schema_editor):
    Member = apps.get_model('accounts', 'Member')
    User = apps.get_model('auth', 'User')

    for member_id, (new_email, new_username) in MEMBER_EMAILS.items():
        try:
            member = Member.objects.select_related('user').get(member_id=member_id)
            user = member.user
            changed = False
            if user.email != new_email:
                user.email = new_email
                changed = True
            if user.username != new_username:
                user.username = new_username
                changed = True
            if changed:
                user.save()
        except Member.DoesNotExist:
            pass


def reverse_sync(apps, schema_editor):
    pass  # No reverse needed


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_globalsetting_qr_code'),
    ]


    operations = [
        migrations.RunPython(sync_emails, reverse_sync),
    ]

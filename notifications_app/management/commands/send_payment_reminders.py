from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import Member, GlobalSetting
from deposits.models import Deposit


class Command(BaseCommand):
    help = 'Sends payment reminder emails to members who have 3 or fewer days remaining for monthly payment.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        cur_year = today.year
        cur_month = today.month

        setting = GlobalSetting.get_settings()
        initial_days = setting.remaining_days or 0
        start_date = setting.remaining_days_updated_at or today

        elapsed = (today - start_date).days
        days_left = initial_days - elapsed

        self.stdout.write(self.style.NOTICE(
            f"Checking payment reminders for Month {cur_month}/{cur_year}. Days left: {days_left} (Elapsed: {elapsed})"
        ))

        # Check if remaining days is <= 3
        if days_left > 3:
            self.stdout.write(self.style.SUCCESS(
                f"Skipping emails — {days_left} days remaining (> 3 days limit)."
            ))
            return

        all_members = Member.objects.select_related('user').all()
        sent_count = 0

        for m in all_members:
            has_paid = Deposit.objects.filter(
                member=m,
                saving_month=cur_month,
                saving_year=cur_year
            ).exclude(status='rejected').exists()


            if not has_paid and m.user.email:
                name = f"{m.user.first_name} {m.user.last_name}".strip() or m.user.username
                subject = f"⚠️ Action Required: {days_left} Days Left for Payment — Thimi Investment Group"

                html_message = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
                    <div style="text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 16px; margin-bottom: 20px;">
                        <h2 style="color: #1e293b; margin: 0;">Thimi Investment Group</h2>
                        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">Automated Daily Payment Reminder</p>
                    </div>
                    
                    <p style="font-size: 16px; color: #1e293b;">Dear <strong>{name}</strong> ({m.member_id}),</p>
                    
                    <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 16px; margin: 20px 0; border-radius: 4px;">
                        <p style="margin: 0; font-size: 15px; color: #991b1b;">
                            Your monthly payment/claim for <strong>Month {cur_month}, {cur_year}</strong> is currently pending.
                        </p>
                        <p style="margin: 8px 0 0 0; font-weight: bold; color: #dc2626; font-size: 17px;">
                            ⌛ Deadline Alert: Only {days_left} Day(s) Remaining!
                        </p>
                    </div>

                    <div style="background: #f8fafc; padding: 14px; border-radius: 6px; margin-bottom: 20px; font-size: 13px; color: #475569;">
                        <strong>📌 Fine Rules:</strong><br/>
                        • First 5 days: Rs. 0 fine<br/>
                        • Days 6 to 10: Rs. 200 fine<br/>
                        • After 10 days: Rs. 100 fine
                    </div>

                    <div style="text-align: center; margin-top: 24px;">
                        <a href="https://thimi-investment-aa.up.railway.app/login/" style="background-color: #2563eb; color: #ffffff; text-decoration: none; padding: 12px 28px; font-size: 15px; font-weight: bold; border-radius: 6px; display: inline-block;">
                            Log In & Pay / Claim Now
                        </a>
                    </div>
                </div>
                """

                try:
                    send_mail(
                        subject=subject,
                        message=f"Dear {name}, your monthly payment for {cur_month}/{cur_year} is pending ({days_left} days left). Please log in to pay/claim.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[m.user.email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    sent_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Sent reminder email to {name} ({m.user.email})"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed sending to {m.user.email}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Finished. Total reminder emails sent: {sent_count}"))

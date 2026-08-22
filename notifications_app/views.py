import datetime
import urllib.request as _urllib_req
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from accounts.models import User, Member, GlobalSetting
from deposits.models import Deposit
from .models import SystemNotification


class SystemNotificationListView(APIView):
    """
    GET /api/notifications/messages/
    Returns list of system notifications and profile update alerts for Admin.
    Supports ?unread_only=true
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = SystemNotification.objects.all()
        unread_only = request.query_params.get('unread_only', '').lower() == 'true'
        if unread_only:
            qs = qs.filter(is_read=False)
        notifs = qs[:100]
        data = []
        for n in notifs:
            data.append({
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "category": n.category,
                "user": n.user.username if n.user else None,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
                "is_read": n.is_read,
            })
        unread_count = SystemNotification.objects.filter(is_read=False).count()
        return Response({"results": data, "unread_count": unread_count})

    def patch(self, request):
        """PATCH /api/notifications/messages/ — mark a notification as read"""
        notif_id = request.data.get("id")
        mark_all = request.data.get("mark_all", False)
        if mark_all:
            SystemNotification.objects.filter(is_read=False).update(is_read=True)
            return Response({"message": "All notifications marked as read."})
        if notif_id:
            try:
                n = SystemNotification.objects.get(id=notif_id)
                n.is_read = True
                n.save()
                return Response({"message": "Notification marked as read."})
            except SystemNotification.DoesNotExist:
                return Response({"detail": "Not found."}, status=404)
        return Response({"detail": "Provide 'id' or 'mark_all: true'."}, status=400)


class SendMemberMessageView(APIView):
    """
    POST /api/notifications/send-message/
    Allows any authenticated member to send a message to the admin.
    Stores the message as a SystemNotification with category='message'.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subject = (request.data.get("subject") or "").strip()
        body = (request.data.get("body") or "").strip()

        if not subject or not body:
            return Response(
                {"detail": "Both subject and message body are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        # Get member ID if available
        try:
            member = Member.objects.get(user=user)
            member_id = member.member_id
        except Member.DoesNotExist:
            member_id = user.username

        full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        SystemNotification.objects.create(
            user=user,
            title=f"📩 {subject} — from {full_name} ({member_id})",
            message=body,
            category="message",
        )

        return Response({"message": "Your message has been sent to the admin successfully."})


class AdminReplyMessageView(APIView):
    """
    GET  /api/notifications/reply/<id>/  — fetch single notification detail
    POST /api/notifications/reply/<id>/  — reply by email to the member
    """
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            n = SystemNotification.objects.get(id=pk)
        except SystemNotification.DoesNotExist:
            return Response({"detail": "Message not found."}, status=404)

        # Get member email
        reply_to_email = ""
        full_name = ""
        if n.user:
            email = (n.user.email or "").strip()
            username = (n.user.username or "").strip()
            if email and "@" in email:
                reply_to_email = email
            elif username and "@" in username:
                reply_to_email = username
            full_name = f"{n.user.first_name} {n.user.last_name}".strip() or n.user.username

        # Mark as read when admin opens it
        if not n.is_read:
            n.is_read = True
            n.save()

        return Response({
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "category": n.category,
            "user": n.user.username if n.user else None,
            "reply_to_email": reply_to_email,
            "member_name": full_name,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    def post(self, request, pk):
        try:
            n = SystemNotification.objects.get(id=pk)
        except SystemNotification.DoesNotExist:
            return Response({"detail": "Message not found."}, status=404)

        reply_text = (request.data.get("reply") or "").strip()
        if not reply_text:
            return Response({"detail": "Reply message cannot be empty."}, status=400)

        # Resolve member email
        reply_to_email = ""
        member_name = "Member"
        if n.user:
            email = (n.user.email or "").strip()
            username = (n.user.username or "").strip()
            if email and "@" in email:
                reply_to_email = email
            elif username and "@" in username:
                reply_to_email = username
            member_name = f"{n.user.first_name} {n.user.last_name}".strip() or n.user.username

        if not reply_to_email:
            return Response({"detail": "No valid email found for this member."}, status=400)

        subject = f"Re: {n.title} — Thimi Investment Group"

        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;
                    border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
            <div style="border-bottom: 2px solid #2563eb; padding-bottom: 14px; margin-bottom: 20px;">
                <h2 style="margin:0; color:#1e293b;">Thimi Investment Group</h2>
                <p style="color:#64748b; font-size:13px; margin-top:4px;">Admin Reply</p>
            </div>
            <p style="font-size:15px; color:#1e293b;">Dear <strong>{member_name}</strong>,</p>
            <div style="background:#f0f7ff; border-left:4px solid #2563eb; padding:16px; border-radius:4px; margin:16px 0;">
                <p style="margin:0; white-space:pre-wrap; color:#1e40af;">{reply_text}</p>
            </div>
            <hr style="border:none; border-top:1px solid #e2e8f0; margin:20px 0;"/>
            <p style="font-size:12px; color:#94a3b8; text-align:center; margin:0;">
                — Thimi Investment Group Admin — Do not reply to this automated email.
            </p>
        </div>
        """

        try:
            send_mail(
                subject=subject,
                message=reply_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reply_to_email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            return Response({"detail": f"Email delivery failed: {str(e)}"}, status=500)

        # Mark as read
        if not n.is_read:
            n.is_read = True
            n.save()

        return Response({
            "message": f"Reply sent successfully to {reply_to_email}.",
            "sent_to": reply_to_email,
        })



def get_member_email(member):
    """Returns valid email for a member, checking user.email then fallback to username if it is an email."""
    email = (member.user.email or '').strip()
    if email and '@' in email:
        return email
    username = (member.user.username or '').strip()
    if username and '@' in username:
        return username
    return email


def calculate_member_payment_status():
    """
    Helper to find members who haven't submitted/approved payment for the current month
    and calculate their remaining days based on GlobalSetting.
    """
    today = timezone.now().date()
    cur_year = today.year
    cur_month = today.month

    setting = GlobalSetting.get_settings()
    initial_days = setting.remaining_days or 0
    start_date = setting.remaining_days_updated_at or today

    elapsed = (today - start_date).days
    days_left = initial_days - elapsed

    all_members = Member.objects.select_related('user').all()
    pending_members = []
    urgent_members = [] # <= 3 days left

    for m in all_members:
        # Check if member has an approved or submitted deposit for current year/month
        has_paid = Deposit.objects.filter(
            member=m,
            saving_month=cur_month,
            saving_year=cur_year
        ).exclude(status='rejected').exists()

        email = get_member_email(m)
        if not has_paid:
            member_info = {
                'id': m.id,
                'member_id': m.member_id,
                'name': f"{m.user.first_name} {m.user.last_name}".strip() or m.user.username,
                'email': email,
                'days_left': days_left,
                'elapsed': elapsed,
            }
            pending_members.append(member_info)
            if days_left <= 3:
                urgent_members.append(member_info)

    return {
        'total_members': all_members.count(),
        'pending_count': len(pending_members),
        'urgent_count': len(urgent_members),
        'days_left': days_left,
        'cur_month': cur_month,
        'cur_year': cur_year,
        'pending_members': pending_members,
        'urgent_members': urgent_members,
        'smtp_user': getattr(settings, 'EMAIL_HOST_USER', ''),
    }


class NotificationStatusView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            data = calculate_member_payment_status()
            return Response(data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'detail': f"Status calculation error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendPaymentRemindersView(APIView):
    """
    Sends payment reminder emails to members who have pending payments (especially <= 3 days remaining).
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            target = request.data.get('target', 'urgent')  # 'urgent' (<=3 days) or 'all_pending'
            data = calculate_member_payment_status()

            recipients = data['urgent_members'] if target == 'urgent' else data['pending_members']

            if not recipients:
                return Response({'message': 'No members found matching the criteria.', 'sent_count': 0})

            sent_count = 0
            failed = []

            cur_month = data['cur_month']
            cur_year = data['cur_year']
            days_left = data['days_left']

            # Fetch setting to calculate days overdue correctly
            setting = GlobalSetting.get_settings()
            initial_days = setting.remaining_days or 0

            # Month name for display
            month_names = [
                '', 'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]
            month_name = month_names[cur_month] if 1 <= cur_month <= 12 else str(cur_month)

            # ---- Fixed remaining-days display (never shows negative) ----
            if days_left > 0:
                remaining_text = f"⏳ {days_left} Day(s) Remaining Before Deadline"
                days_left_display = days_left
            elif days_left == 0:
                remaining_text = "⏳ Deadline is today"
                days_left_display = 0
            else:
                remaining_text = f"⏳ Deadline passed {abs(days_left)} day(s) ago"
                days_left_display = 0   # for table display

            # Urgency color — treat overdue (≤ 0) the same as urgent
            is_urgent = days_left <= 3
            urgency_color = '#dc2626' if is_urgent else '#d97706'
            urgency_bg = '#fef2f2' if is_urgent else '#fffbeb'
            urgency_border = '#dc2626' if is_urgent else '#f59e0b'

            MONTHLY_DEPOSIT = 5000  # Rs. 5,000 standard monthly deposit

            for m in recipients:
                email = m['email']
                if not email or '@' not in email:
                    continue

                elapsed = m.get('elapsed', 0)
                days_overdue = max(0, elapsed - initial_days)

                # Calculate fine using same rules as dashboard (days overdue after deadline)
                if days_overdue == 0:
                    fine = 0
                    fine_status = 'Payment deadline today — No fine yet'
                    fine_color = '#16a34a'
                elif days_overdue <= 10:
                    fine = 200
                    fine_status = f'Day {days_overdue} overdue — Flat fine Rs. 200 (Days 1–10)'
                    fine_color = '#d97706'
                else:
                    daily_fine_days = days_overdue - 10
                    fine = 200 + daily_fine_days * 100
                    fine_status = f'Day {days_overdue} overdue — Rs. 200 + Rs. 100/day × {daily_fine_days} days'
                    fine_color = '#dc2626'

                total_due = MONTHLY_DEPOSIT + fine

                subject = f"⚠️ Action Required: Payment Pending for {month_name} {cur_year} — Thimi Investment"

                html_message = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f1f5f9;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;max-width:600px;">

      <!-- Header -->
      <tr>
        <td style="background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);padding:32px 40px;text-align:center;">
          <h1 style="color:#ffffff;margin:0;font-size:22px;font-weight:700;letter-spacing:0.5px;">Thimi Investment Group</h1>
          <p style="color:#bfdbfe;margin:6px 0 0 0;font-size:13px;letter-spacing:1px;text-transform:uppercase;">Monthly Payment Reminder</p>
        </td>
      </tr>

      <!-- Body -->
      <tr>
        <td style="padding:36px 40px;">

          <!-- Greeting -->
          <p style="font-size:16px;color:#1e293b;margin:0 0 8px 0;">Dear <strong>{m['name']}</strong>,</p>
          <p style="font-size:14px;color:#64748b;margin:0 0 28px 0;">Member ID: <strong>{m['member_id']}</strong></p>

          <!-- Alert Banner -->
          <div style="background:{urgency_bg};border:1px solid {urgency_border};border-left:5px solid {urgency_border};border-radius:8px;padding:18px 20px;margin-bottom:28px;">
            <p style="margin:0;font-size:15px;color:#1e293b;font-weight:600;">
              ⚠️ Your monthly payment for <span style="color:{urgency_color};">{month_name} {cur_year}</span> has not been submitted yet.
            </p>
            <p style="margin:10px 0 0 0;font-size:14px;color:{urgency_color};font-weight:700;">
              {remaining_text}
            </p>
          </div>

          <!-- Amount Due Box -->
          <div style="background:#fff7ed;border:2px solid #fb923c;border-radius:10px;padding:22px 24px;margin-bottom:28px;text-align:center;">
            <p style="margin:0 0 4px 0;font-size:13px;color:#92400e;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Total Amount Due</p>
            <p style="margin:0;font-size:38px;font-weight:800;color:#dc2626;">Rs. {total_due:,.0f}</p>
            <p style="margin:8px 0 0 0;font-size:13px;color:#78350f;">
              Monthly Deposit: <strong>Rs. {MONTHLY_DEPOSIT:,.0f}</strong>
              &nbsp;+&nbsp;
              Fine: <strong style="color:{fine_color};">Rs. {fine:,.0f}</strong>
            </p>
            <p style="margin:6px 0 0 0;font-size:12px;color:{fine_color};">{fine_status}</p>
          </div>

          <!-- Payment Info Table -->
          <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;">
            <tr style="background:#f8fafc;">
              <td style="padding:12px 16px;font-size:13px;color:#64748b;font-weight:600;border-bottom:1px solid #e2e8f0;">Period</td>
              <td style="padding:12px 16px;font-size:13px;color:#1e293b;font-weight:600;border-bottom:1px solid #e2e8f0;">{month_name} {cur_year}</td>
            </tr>
            <tr>
              <td style="padding:12px 16px;font-size:13px;color:#64748b;border-bottom:1px solid #e2e8f0;">Days Elapsed</td>
              <td style="padding:12px 16px;font-size:13px;color:#1e293b;border-bottom:1px solid #e2e8f0;">{elapsed} day(s)</td>
            </tr>
            <tr style="background:#f8fafc;">
              <td style="padding:12px 16px;font-size:13px;color:#64748b;border-bottom:1px solid #e2e8f0;">Days Remaining</td>
              <td style="padding:12px 16px;font-size:13px;font-weight:700;color:{urgency_color};border-bottom:1px solid #e2e8f0;">{days_left} day(s)</td>
            </tr>
            <tr>
              <td style="padding:12px 16px;font-size:13px;color:#64748b;">Current Fine</td>
              <td style="padding:12px 16px;font-size:13px;font-weight:700;color:{fine_color};">Rs. {fine:,.0f}</td>
            </tr>
          </table>

          <!-- Fine Rules -->
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:18px 20px;margin-bottom:28px;">
            <p style="margin:0 0 12px 0;font-size:13px;color:#1e293b;font-weight:700;">📌 Fine Structure</p>
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="padding:5px 0;font-size:13px;color:#475569;">Days 1–5 (Grace Period)</td>
                <td style="padding:5px 0;font-size:13px;color:#16a34a;font-weight:600;text-align:right;">Rs. 0</td>
              </tr>
              <tr>
                <td style="padding:5px 0;font-size:13px;color:#475569;">Days 6–10</td>
                <td style="padding:5px 0;font-size:13px;color:#d97706;font-weight:600;text-align:right;">Rs. 200 (flat)</td>
              </tr>
              <tr>
                <td style="padding:5px 0;font-size:13px;color:#475569;">After Day 10</td>
                <td style="padding:5px 0;font-size:13px;color:#dc2626;font-weight:600;text-align:right;">Rs. 100 / day additional</td>
              </tr>
            </table>
          </div>

          <p style="font-size:14px;color:#334155;margin:0 0 28px 0;">
            Please log into your member dashboard and submit your payment claim immediately to avoid further accumulation of fines.
          </p>

          <!-- CTA Button -->
          <div style="text-align:center;margin-bottom:8px;">
            <a href="https://www.thimiinvestment.com/member/claim-payment/"
               style="background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#ffffff;text-decoration:none;padding:14px 36px;font-size:15px;font-weight:700;border-radius:8px;display:inline-block;letter-spacing:0.3px;">
              Submit Payment Now →
            </a>
          </div>

        </td>
      </tr>

      <!-- Footer -->
      <tr>
        <td style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:20px 40px;text-align:center;">
          <p style="margin:0;font-size:12px;color:#94a3b8;">
            This is an automated notification from Thimi Investment Group.<br/>
            Please do not reply to this email. For queries, contact your group admin.
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""

                plain_text = (
                    f"Dear {m['name']} ({m['member_id']}),\n\n"
                    f"Your monthly payment for {month_name} {cur_year} is PENDING.\n\n"
                    f"Total Amount Due: Rs. {total_due:,.0f}\n"
                    f"  - Monthly Deposit: Rs. {MONTHLY_DEPOSIT:,.0f}\n"
                    f"  - Current Fine:    Rs. {fine:,.0f}\n\n"
                    f"Days Elapsed: {elapsed}\n"
                    f"{remaining_text}\n\n"
                    f"Please log in at https://www.thimiinvestment.com/member/claim-payment/ to submit your payment.\n\n"
                    f"Fine Rules: Days 1-5: Rs.0 | Days 6-10: Rs.200 | After Day 10: Rs.100/day\n\n"
                    f"— Thimi Investment Group"
                )

                try:
                    send_mail(
                        subject=subject,
                        message=plain_text,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    sent_count += 1
                except Exception as e:
                    failed.append({'member': m['name'], 'email': email, 'error': str(e)})

            return Response({
                'message': f"Sent {sent_count} reminder email(s) successfully.",
                'sent_count': sent_count,
                'failed_count': len(failed),
                'failed_details': failed
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'detail': f"Send reminders error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendBroadcastEmailView(APIView):
    """
    Allows admin to send custom broadcast emails to members or test email address.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            subject = request.data.get('subject')
            message_body = request.data.get('message')
            target_group = request.data.get('target', 'all') # 'all', 'active', 'custom'
            custom_email = (request.data.get('custom_email') or '').strip()

            if not subject or not message_body:
                return Response({'detail': 'Subject and message body are required.'}, status=status.HTTP_400_BAD_REQUEST)

            recipients = []
            if target_group == 'custom':
                if not custom_email:
                    return Response({'detail': 'Please provide recipient email address(es) for custom email target.'}, status=status.HTTP_400_BAD_REQUEST)
                recipients = [e.strip() for e in custom_email.split(',') if e.strip() and '@' in e.strip()]
            else:
                # 1. Check Member profiles
                members = Member.objects.select_related('user').all()
                if target_group == 'active':
                    members = members.filter(is_active_member=True)

                for m in members:
                    e = get_member_email(m)
                    if e and '@' in e:
                        recipients.append(e)

                # 2. Check all User objects as fallback
                users = User.objects.all()
                if target_group == 'active':
                    users = users.filter(is_active=True)

                for u in users:
                    u_email = (u.email or '').strip()
                    u_user = (u.username or '').strip()
                    if u_email and '@' in u_email:
                        recipients.append(u_email)
                    elif u_user and '@' in u_user:
                        recipients.append(u_user)

            # Deduplicate while preserving order
            recipients = list(dict.fromkeys(recipients))

            if not recipients:
                return Response({'detail': 'No valid recipient email addresses found.'}, status=status.HTTP_400_BAD_REQUEST)

            sent_count = 0
            failed = []

            for email in recipients:
                try:
                    send_mail(
                        subject=subject,
                        message=message_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False
                    )
                    sent_count += 1
                except Exception as e:
                    import traceback
                    print(f"Failed to send email to {email}: {e}")
                    failed.append({'email': email, 'error': str(e)})

            recipient_summary = ", ".join(recipients[:5])
            if len(recipients) > 5:
                recipient_summary += f" and {len(recipients) - 5} more"

            msg = f"Broadcast process finished. Sent: {sent_count}, Failed: {len(failed)}."
            if sent_count > 0:
                msg = f"Broadcast email sent to {sent_count} recipient(s) [{recipient_summary}]."
            elif len(failed) > 0:
                msg = f"Could not deliver to recipient(s). Error: {failed[0]['error']}"

            return Response({
                'message': msg,
                'sent_count': sent_count,
                'recipients': recipients,
                'failed_count': len(failed),
                'failed_details': failed
            }, status=status.HTTP_200_OK if sent_count > 0 else status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'detail': f"Send broadcast error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ServerIPView(APIView):
    """
    Temporary diagnostic endpoint: returns Railway's outbound IP address.
    Used for whitelisting in cPanel CSF Firewall.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            ip = _urllib_req.urlopen('https://api.ipify.org', timeout=5).read().decode()
            return Response({'server_outbound_ip': ip, 'message': 'Add this IP to CSF Firewall whitelist in WHM'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from .teams_utils import create_microsoft_teams_meeting


class GenerateTeamsMeetingView(APIView):
    """
    POST /api/notifications/generate-teams-meeting/
    Auto-generates a Microsoft Teams online meeting link via Microsoft Graph API.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        meeting_date = (request.data.get("meeting_date") or "").strip()
        meeting_time = (request.data.get("meeting_time") or "").strip()
        subject = (request.data.get("subject") or "Thimi Investment Group General Meeting").strip()

        start_datetime_str = None
        if meeting_date:
            if meeting_time:
                start_datetime_str = f"{meeting_date} {meeting_time}"
            else:
                start_datetime_str = meeting_date

        res = create_microsoft_teams_meeting(
            subject=subject,
            start_datetime_str=start_datetime_str
        )

        if res.get("success"):
            return Response({
                "join_url": res["join_url"],
                "meeting_id": res.get("meeting_id", ""),
                "subject": res.get("subject", subject)
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "detail": res.get("error", "Failed to generate Microsoft Teams meeting."),
                "help": res.get("help", "")
            }, status=status.HTTP_400_BAD_REQUEST)


class SendMeetingAnnouncementView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        meeting_date_str = (request.data.get("meeting_date") or "").strip()
        meeting_time     = (request.data.get("meeting_time") or "").strip()
        venue            = (request.data.get("venue") or "").strip()
        meeting_link     = (request.data.get("meeting_link") or request.data.get("zoom_link") or "").strip()
        nepali_date      = (request.data.get("nepali_date") or "").strip()
        agenda           = (request.data.get("agenda") or "").strip()
        custom_note      = (request.data.get("custom_note") or "").strip()

        if not meeting_date_str or not venue:
            return Response(
                {"detail": "meeting_date and venue are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            meeting_dt = datetime.datetime.strptime(meeting_date_str, "%Y-%m-%d")
            meeting_date_fmt = meeting_dt.strftime("%A, %B %d, %Y")
        except ValueError:
            meeting_date_fmt = meeting_date_str

        date_line = meeting_date_fmt
        if nepali_date:
            date_line += " (" + nepali_date + " BS)"
        if meeting_time:
            date_line += " at " + meeting_time

        link_row = ""
        if meeting_link:
            is_teams = "teams." in meeting_link.lower()
            is_zoom = "zoom." in meeting_link.lower()

            if is_teams:
                label = "Join Teams Meeting"
                badge = "🟣 Teams Meeting"
                btn_color = "#4f46e5" # Teams Indigo
            elif is_zoom:
                label = "Join Zoom Meeting"
                badge = "🔵 Zoom Meeting"
                btn_color = "#0284c7" # Zoom Blue
            else:
                label = "Join Online Meeting"
                badge = "🔗 Online Meeting"
                btn_color = "#2563eb"

            link_row = (
                "<tr><td style='padding:8px 0;border-top:1px solid #bae6fd;'><span style='font-size:13px;color:#64748b;font-weight:600;'>" + badge + "</span></td>"
                "<td style='padding:8px 0;border-top:1px solid #bae6fd;text-align:right;'><a href='" + meeting_link + "' target='_blank' style='display:inline-block;background:" + btn_color + ";color:#ffffff;font-size:12px;font-weight:bold;padding:5px 14px;border-radius:5px;text-decoration:none;'>" + label + "</a></td></tr>"
            )

        agenda_html = ""
        if agenda:
            items = [line.strip() for line in agenda.split("\n") if line.strip()]
            li_items = "".join("<li style='margin-bottom:6px;'>" + item + "</li>" for item in items)
            agenda_html = (
                "<div style='margin-top:20px;'>"
                "<p style='font-size:14px;font-weight:700;color:#1e293b;margin:0 0 8px 0;'>📋 Meeting Agenda:</p>"
                "<ol style='margin:0;padding-left:20px;font-size:13px;color:#334155;line-height:1.8;'>" + li_items + "</ol>"
                "</div>"
            )

        note_html = ""
        if custom_note:
            note_html = (
                "<div style='background:#eff6ff;border-left:4px solid #2563eb;border-radius:4px;padding:12px 16px;margin-top:16px;'>"
                "<p style='font-size:13px;color:#1e3a8a;margin:0;'><strong>Note from Admin:</strong> " + custom_note + "</p>"
                "</div>"
            )

        members = Member.objects.select_related("user").filter(user__is_active=True)
        sent_count = 0
        failed = []

        for m in members:
            email = m.user.email
            name = m.user.get_full_name() or m.user.username
            if not email or "@" not in email:
                continue

            subject = "📅 Meeting Notice: " + meeting_date_fmt + " — Thimi Investment Group"

            html_message = (
                "<!DOCTYPE html><html><body style='margin:0;padding:0;background:#f1f5f9;'>"
                "<table width='100%' cellpadding='0' cellspacing='0' style='background:#f1f5f9;padding:32px 0;'>"
                "<tr><td align='center'>"
                "<table width='600' cellpadding='0' cellspacing='0' style='background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;max-width:600px;'>"
                "<tr><td style='background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);padding:32px 40px;text-align:center;'>\""
                "<h1 style='color:#ffffff;margin:0;font-size:22px;font-weight:700;'>Thimi Investment Group</h1>"
                "<p style='color:#bfdbfe;margin:6px 0 0 0;font-size:13px;text-transform:uppercase;'>Meeting Announcement</p>"
                "</td></tr>"
                "<tr><td style='padding:32px 40px;'>"
                "<p style='font-size:16px;color:#1e293b;margin:0 0 4px 0;'>Dear <strong>" + name + "</strong>,</p>"
                "<p style='font-size:13px;color:#64748b;margin:0 0 20px 0;'>Member ID: " + str(m.member_id) + "</p>"
                "<p style='font-size:14px;color:#334155;line-height:1.7;margin:0 0 20px 0;'>You are cordially invited to attend the upcoming <strong>General Meeting</strong> of Thimi Investment Group. Your presence is important.</p>"
                "<div style='background:#f0f9ff;border:2px solid #0ea5e9;border-radius:10px;padding:24px;margin-bottom:20px;'>"
                "<p style='font-size:13px;font-weight:700;color:#0369a1;text-transform:uppercase;margin:0 0 16px 0;'>📅 Meeting Details</p>"
                "<table width='100%' cellpadding='0' cellspacing='0'>"
                "<tr><td style='padding:8px 0;border-bottom:1px solid #bae6fd;'><span style='font-size:13px;color:#64748b;font-weight:600;'>📆 Date &amp; Time</span></td>"
                "<td style='padding:8px 0;border-bottom:1px solid #bae6fd;text-align:right;'><span style='font-size:13px;color:#0c4a6e;font-weight:700;'>" + date_line + "</span></td></tr>"
                "<tr><td style='padding:8px 0;'><span style='font-size:13px;color:#64748b;font-weight:600;'>📍 Venue</span></td>"
                "<td style='padding:8px 0;text-align:right;'><span style='font-size:13px;color:#0c4a6e;font-weight:700;'>" + venue + "</span></td></tr>"
                + link_row +
                "</table></div>"
                + agenda_html + note_html +
                "<p style='font-size:13px;color:#475569;margin:24px 0 0 0;'>Please inform the admin if you are unable to attend.</p>"
                "</td></tr>"
                "<tr><td style='padding:0 40px 28px 40px;text-align:center;'>"
                "<a href='https://www.thimiinvestment.com/login/' style='display:inline-block;background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#fff;text-decoration:none;padding:13px 36px;border-radius:8px;font-size:14px;font-weight:700;'>View Member Dashboard</a>"
                "</td></tr>"
                "<tr><td style='background:#f8fafc;padding:20px 40px;text-align:center;border-top:1px solid #e2e8f0;'>"
                "<p style='font-size:11px;color:#94a3b8;margin:0;'>Official announcement from Thimi Investment Group. Do not reply.</p>"
                "</td></tr></table></td></tr></table></body></html>"
            )

            try:
                send_mail(
                    subject=subject,
                    message="Dear " + name + ", meeting on " + date_line + " at " + venue + (" (Meeting Link: " + meeting_link + ")" if meeting_link else "") + ".",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                sent_count += 1
            except Exception as e:
                failed.append({"email": email, "error": str(e)})

        return Response({
            "message": "Meeting announcement sent to " + str(sent_count) + " member(s).",
            "sent_count": sent_count,
            "failed_count": len(failed),
            "failed_details": failed,
        }, status=status.HTTP_200_OK)


import datetime
import socket
import urllib.request as _urllib_req

from smtplib import SMTPException


def email_error_detail(exc):
    """Return an actionable, credential-safe SMTP error for the admin UI."""
    text = str(exc)
    if isinstance(exc, OSError) and getattr(exc, 'errno', None) == 101:
        return f"SMTP network is unreachable ({settings.EMAIL_HOST}:{settings.EMAIL_PORT}). Check Railway outbound SMTP access; Gmail credentials are not the cause."
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return f"SMTP connection timed out ({settings.EMAIL_HOST}:{settings.EMAIL_PORT}). Check Railway egress and Gmail SMTP availability."
    if isinstance(exc, SMTPException):
        return f"Gmail SMTP rejected the request: {text}"
    return f"Email delivery failed: {text}"
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
            return Response({"detail": email_error_detail(e)}, status=502)

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
            target = request.data.get('target', 'urgent') # 'urgent' (<=3 days) or 'all_pending'
            data = calculate_member_payment_status()

            recipients = data['urgent_members'] if target == 'urgent' else data['pending_members']

            if not recipients:
                return Response({'message': 'No members found matching the criteria.', 'sent_count': 0})

            sent_count = 0
            failed = []

            cur_month = data['cur_month']
            cur_year = data['cur_year']
            days_left = data['days_left']

            for m in recipients:
                email = m['email']
                if not email or '@' not in email:
                    continue

                subject = f"⚠️ Payment Reminder: {days_left} Days Remaining — Thimi Investment Group"

                html_message = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
                    <div style="text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 16px; margin-bottom: 20px;">
                        <h2 style="color: #1e293b; margin: 0;">Thimi Investment Group</h2>
                        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">Monthly Payment Notification</p>
                    </div>
                    
                    <p style="font-size: 16px; color: #1e293b;">Dear <strong>{m['name']}</strong> ({m['member_id']}),</p>
                    
                    <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 20px 0; border-radius: 4px;">
                        <p style="margin: 0; font-size: 15px; color: #1e40af;">
                            This is a friendly reminder that your monthly investment/deposit for <strong>Month {cur_month}, {cur_year}</strong> is currently pending.
                        </p>
                        <p style="margin: 8px 0 0 0; font-weight: bold; color: #dc2626; font-size: 16px;">
                            ⌛ Time Remaining: {days_left} Day(s) Left
                        </p>
                    </div>

                    <div style="background: #f8fafc; padding: 14px; border-radius: 6px; margin-bottom: 20px; font-size: 13px; color: #475569;">
                        <strong>📌 Fine Structure Info:</strong><br/>
                        • First 5 days: Rs. 0 fine<br/>
                        • Days 6 to 10: Rs. 200 fine<br/>
                        • After 10 days: Rs. 100 fine
                    </div>

                    <p style="font-size: 14px; color: #334155;">
                        Please log into your dashboard to claim or submit your payment record as soon as possible.
                    </p>

                    <div style="text-align: center; margin-top: 24px;">
                        <a href="https://thimi-investment-aa.up.railway.app/login/" style="background-color: #2563eb; color: #ffffff; text-decoration: none; padding: 12px 28px; font-size: 15px; font-weight: bold; border-radius: 6px; display: inline-block;">
                            Log Into Member Dashboard
                        </a>
                    </div>

                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 28px 0 16px 0;" />
                    <p style="font-size: 12px; color: #94a3b8; text-align: center; margin: 0;">
                        Thimi Investment Group System Notification — Please do not reply directly to this automated email.
                    </p>
                </div>
                """

                try:
                    send_mail(
                        subject=subject,
                        message=f"Dear {m['name']}, your payment for Month {cur_month}/{cur_year} is pending ({days_left} days remaining). Please log into your dashboard.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False
                    )
                    sent_count += 1
                except Exception as e:
                    failed.append({'member': m['name'], 'email': email, 'error': email_error_detail(e)})

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
                    print(f"Failed to send email to {email}: {email_error_detail(e)}")
                    failed.append({'email': email, 'error': email_error_detail(e)})

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


class SMTPDiagnosticView(APIView):
    """Check Gmail SMTP DNS/TCP reachability without exposing credentials."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        host = settings.EMAIL_HOST
        port = settings.EMAIL_PORT
        try:
            addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            with socket.create_connection((host, port), timeout=settings.EMAIL_TIMEOUT):
                pass
            return Response({
                'ok': True,
                'host': host,
                'port': port,
                'resolved_addresses': len(addresses),
                'message': 'SMTP host is reachable. Credentials were not tested or exposed.',
            })
        except Exception as exc:
            return Response({
                'ok': False,
                'host': host,
                'port': port,
                'error': email_error_detail(exc),
                'message': 'Network reachability failed before SMTP authentication.',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


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


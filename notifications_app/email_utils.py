import threading
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User, Member


def get_admin_emails():
    """Returns list of valid email addresses for staff/admin users."""
    admins = User.objects.filter(is_staff=True)
    admin_emails = []
    for a in admins:
        e = (a.email or "").strip()
        u = (a.username or "").strip()
        if e and "@" in e:
            admin_emails.append(e)
        elif u and "@" in u:
            admin_emails.append(u)
    # Default fallback
    fallback = (getattr(settings, "EMAIL_HOST_USER", "") or "").strip()
    if fallback and "@" in fallback and fallback not in admin_emails:
        admin_emails.append(fallback)
    return list(dict.fromkeys(admin_emails))


def get_user_email(user):
    """Returns email for a Django user (checking email first, then username)."""
    if not user:
        return None
    e = (user.email or "").strip()
    if e and "@" in e:
        return e
    u = (user.username or "").strip()
    if u and "@" in u:
        return u
    return None


def send_email_async(subject, text_message, recipient_list, html_message=None):
    """Sends email asynchronously in a separate thread to prevent blocking HTTP requests."""
    def _send():
        try:
            send_mail(
                subject=subject,
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"[Email Delivery Error] Failed to send '{subject}' to {recipient_list}: {e}")

    thread = threading.Thread(target=_send)
    thread.daemon = True
    thread.start()


# =====================================================================
# DEPOSIT / PAYMENT CLAIM EMAIL NOTIFICATIONS
# =====================================================================

def send_deposit_claimed_emails(deposit):
    """
    Triggers when a member submits a new payment claim.
    Sends confirmation email to the user AND alert email to admins.
    """
    user = deposit.member.user
    member_name = f"{user.first_name} {user.last_name}".strip() or user.username
    member_id = deposit.member.member_id
    user_email = get_user_email(user)

    # 1. Email to User
    if user_email:
        user_subject = f"✅ Payment Claim Received: Month {deposit.saving_month}/{deposit.saving_year} — Thimi Investment"
        user_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
            <div style="text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 16px; margin-bottom: 20px;">
                <h2 style="color: #1e293b; margin: 0;">Thimi Investment Group</h2>
                <p style="color: #64748b; font-size: 14px; margin-top: 4px;">Payment Claim Confirmation</p>
            </div>
            <p style="font-size: 16px; color: #1e293b;">Dear <strong>{member_name}</strong> ({member_id}),</p>
            <p style="font-size: 15px; color: #334155;">Your payment claim has been submitted successfully and is currently <strong>Pending Verification</strong> by our admin team.</p>

            <div style="background: #f8fafc; border: 1px solid #cbd5e1; padding: 16px; border-radius: 6px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #1e293b;">Claim Details:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 14px;">
                    <li><strong>Month / Year:</strong> Month {deposit.saving_month}, {deposit.saving_year}</li>
                    <li><strong>Amount Claimed:</strong> Rs. {deposit.amount:,.2f}</li>
                    <li><strong>Payment Date:</strong> {deposit.payment_date or 'N/A'}</li>
                    <li><strong>Status:</strong> <span style="color: #d97706; font-weight: bold;">Pending Verification</span></li>
                </ul>
            </div>

            <p style="font-size: 14px; color: #475569;">You will receive an email update once your payment claim has been verified.</p>

            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0;" />
            <p style="font-size: 12px; color: #94a3b8; text-align: center; margin: 0;">
                Thimi Investment Group System Notification — Please do not reply directly to this email.
            </p>
        </div>
        """
        user_text = f"Dear {member_name}, your payment claim of Rs. {deposit.amount} for Month {deposit.saving_month}/{deposit.saving_year} has been submitted and is pending verification."
        send_email_async(user_subject, user_text, [user_email], user_html)

    # 2. Email to Admin(s)
    admin_emails = get_admin_emails()
    if admin_emails:
        admin_subject = f"🔔 New Payment Claim Submitted by {member_name} ({member_id})"
        admin_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
            <div style="text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 16px; margin-bottom: 20px;">
                <h2 style="color: #1e293b; margin: 0;">Thimi Investment Group</h2>
                <p style="color: #64748b; font-size: 14px; margin-top: 4px;">Admin Alert: New Payment Claim</p>
            </div>
            <p style="font-size: 15px; color: #1e293b;">Member <strong>{member_name}</strong> (ID: {member_id}) has submitted a new payment claim.</p>

            <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 20px 0; border-radius: 4px;">
                <ul style="margin: 0; padding-left: 20px; color: #1e40af; font-size: 14px;">
                    <li><strong>Member:</strong> {member_name} ({member_id})</li>
                    <li><strong>Month / Year:</strong> Month {deposit.saving_month}, {deposit.saving_year}</li>
                    <li><strong>Amount:</strong> Rs. {deposit.amount:,.2f}</li>
                    <li><strong>Date:</strong> {deposit.payment_date or 'N/A'}</li>
                </ul>
            </div>

            <p style="font-size: 14px; color: #334155;">Please log into the Admin Dashboard to review and approve or reject this claim.</p>

            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0;" />
            <p style="font-size: 12px; color: #94a3b8; text-align: center; margin: 0;">
                Thimi Investment Group Admin Notification.
            </p>
        </div>
        """
        admin_text = f"Member {member_name} ({member_id}) submitted a payment claim of Rs. {deposit.amount} for Month {deposit.saving_month}/{deposit.saving_year}."
        send_email_async(admin_subject, admin_text, admin_emails, admin_html)


def send_deposit_status_email(deposit, status_action, remarks=None):
    """
    Triggers when an Admin approves or rejects a deposit claim.
    Sends status notification email to the user.
    """
    user = deposit.member.user
    user_email = get_user_email(user)
    if not user_email:
        return

    member_name = f"{user.first_name} {user.last_name}".strip() or user.username
    is_approved = status_action.lower() == "approved"

    if is_approved:
        subject = f"🎉 Payment Claim Approved: Month {deposit.saving_month}/{deposit.saving_year} — Thimi Investment"
        status_color = "#16a34a"
        status_title = "Payment Claim Approved!"
        bg_color = "#f0fdf4"
        border_color = "#22c55e"
        msg_body = f"Great news! Your payment claim of <strong>Rs. {deposit.amount:,.2f}</strong> for Month {deposit.saving_month}/{deposit.saving_year} has been <strong>APPROVED</strong> and recorded."
    else:
        subject = f"❌ Payment Claim Rejected: Month {deposit.saving_month}/{deposit.saving_year} — Thimi Investment"
        status_color = "#dc2626"
        status_title = "Payment Claim Rejected"
        bg_color = "#fef2f2"
        border_color = "#ef4444"
        msg_body = f"Your payment claim of <strong>Rs. {deposit.amount:,.2f}</strong> for Month {deposit.saving_month}/{deposit.saving_year} was <strong>REJECTED</strong> by the administrator."

    remarks_html = f"<p style='margin: 10px 0 0 0; font-size: 14px; color: #475569;'><strong>Remarks / Reason:</strong> {remarks or deposit.remarks or 'Not specified'}</p>" if (remarks or deposit.remarks) else ""

    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
        <div style="text-align: center; border-bottom: 2px solid {border_color}; padding-bottom: 16px; margin-bottom: 20px;">
            <h2 style="color: #1e293b; margin: 0;">Thimi Investment Group</h2>
            <p style="color: {status_color}; font-size: 15px; font-weight: bold; margin-top: 4px;">{status_title}</p>
        </div>

        <p style="font-size: 16px; color: #1e293b;">Dear <strong>{member_name}</strong>,</p>

        <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 16px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; font-size: 15px; color: #1e293b;">{msg_body}</p>
            {remarks_html}
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 6px; font-size: 14px; color: #475569;">
            <strong>Claim Summary:</strong><br/>
            • Month/Year: Month {deposit.saving_month}, {deposit.saving_year}<br/>
            • Amount: Rs. {deposit.amount:,.2f}<br/>
            • Current Status: <strong style="color: {status_color};">{status_action.upper()}</strong>
        </div>

        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0;" />
        <p style="font-size: 12px; color: #94a3b8; text-align: center; margin: 0;">
            Thimi Investment Group System Notification — Please do not reply directly to this email.
        </p>
    </div>
    """

    text_message = f"Dear {member_name}, your payment claim of Rs. {deposit.amount} for Month {deposit.saving_month}/{deposit.saving_year} status updated to {status_action.upper()}."
    send_email_async(subject, text_message, [user_email], html_message)


# =====================================================================
# LOAN APPLICATION EMAIL NOTIFICATIONS
# =====================================================================

def send_loan_applied_emails(loan, user):
    """
    Triggers when a member applies for a new loan.
    Sends confirmation email to user AND alert email to admin(s).
    """
    member_name = loan.name or (f"{user.first_name} {user.last_name}".strip() or user.username)
    user_email = get_user_email(user)

    # 1. Email to User
    if user_email:
        user_subject = f"📋 Loan Application Received: Rs. {loan.amount:,.2f} — Thimi Investment"
        user_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
            <div style="text-align: center; border-bottom: 2px solid #2563eb; padding-bottom: 16px; margin-bottom: 20px;">
                <h2 style="color: #1e293b; margin: 0;">Thimi Investment Group</h2>
                <p style="color: #64748b; font-size: 14px; margin-top: 4px;">Loan Application Confirmation</p>
            </div>
            <p style="font-size: 16px; color: #1e293b;">Dear <strong>{member_name}</strong>,</p>
            <p style="font-size: 15px; color: #334155;">Your application for a personal loan has been received and is currently under review by our administration team.</p>

            <div style="background: #f8fafc; border: 1px solid #cbd5e1; padding: 16px; border-radius: 6px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #1e293b;">Application Details:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 14px;">
                    <li><strong>Requested Amount:</strong> Rs. {loan.amount:,.2f}</li>
                    <li><strong>Interest Rate:</strong> {float(loan.annual_interest_rate or 0)*100:.1f}% p.a.</li>
                    <li><strong>Tenure:</strong> {loan.tenure_years or 0} year(s)</li>
                    <li><strong>Status:</strong> <span style="color: #d97706; font-weight: bold;">Pending Review</span></li>
                    <li><strong>Remarks / Purpose:</strong> {loan.remarks or 'N/A'}</li>
                </ul>
            </div>

            <p style="font-size: 14px; color: #475569;">You will be notified via email once your application decision has been finalized.</p>

            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0;" />
            <p style="font-size: 12px; color: #94a3b8; text-align: center; margin: 0;">
                Thimi Investment Group System Notification — Please do not reply directly to this email.
            </p>
        </div>
        """
        user_text = f"Dear {member_name}, your loan application of Rs. {loan.amount} has been received and is pending approval."
        send_email_async(user_subject, user_text, [user_email], user_html)

    # 2. Email to Admin(s)
    admin_emails = get_admin_emails()
    if admin_emails:
        admin_subject = f"📢 New Loan Application Submitted: {member_name} (Rs. {loan.amount:,.2f})"
        admin_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
            <div style="text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 16px; margin-bottom: 20px;">
                <h2 style="color: #1e293b; margin: 0;">Thimi Investment Group</h2>
                <p style="color: #64748b; font-size: 14px; margin-top: 4px;">Admin Alert: New Loan Request</p>
            </div>
            <p style="font-size: 15px; color: #1e293b;">Member <strong>{member_name}</strong> has submitted a new loan request.</p>

            <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 20px 0; border-radius: 4px;">
                <ul style="margin: 0; padding-left: 20px; color: #1e40af; font-size: 14px;">
                    <li><strong>Applicant Name:</strong> {member_name}</li>
                    <li><strong>Requested Amount:</strong> Rs. {loan.amount:,.2f}</li>
                    <li><strong>Interest Rate:</strong> {float(loan.annual_interest_rate or 0)*100:.1f}% p.a.</li>
                    <li><strong>Tenure:</strong> {loan.tenure_years or 0} year(s)</li>
                    <li><strong>Remarks / Purpose:</strong> {loan.remarks or 'N/A'}</li>
                </ul>
            </div>

            <p style="font-size: 14px; color: #334155;">Please log into the Admin Dashboard to review and approve or reject this loan request.</p>

            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0;" />
            <p style="font-size: 12px; color: #94a3b8; text-align: center; margin: 0;">
                Thimi Investment Group Admin Notification.
            </p>
        </div>
        """
        admin_text = f"Member {member_name} applied for a loan of Rs. {loan.amount}."
        send_email_async(admin_subject, admin_text, admin_emails, admin_html)


def send_loan_status_email(loan, status_action, remarks=None):
    """
    Triggers when an Admin updates loan status (Active/Approved or Rejected/Closed).
    Sends status notification email to member.
    """
    # Find user email by matching loan.name to User or Member
    user_email = None
    member_name = loan.name or "Member"

    # Search User by name or username
    for u in User.objects.all():
        full = f"{u.first_name} {u.last_name}".strip()
        if (full and full.lower() == member_name.lower()) or u.username.lower() == member_name.lower():
            user_email = get_user_email(u)
            break

    if not user_email:
        # Check Member table
        for m in Member.objects.select_related('user').all():
            full = f"{m.user.first_name} {m.user.last_name}".strip()
            if (full and full.lower() == member_name.lower()) or m.user.username.lower() == member_name.lower():
                user_email = get_user_email(m.user)
                break

    if not user_email:
        return

    status_str = str(status_action).strip()
    is_approved = status_str.lower() in ("active", "approved")
    is_rejected = status_str.lower() in ("rejected",)

    if is_approved:
        subject = f"🎉 Loan Application Approved: Rs. {loan.amount:,.2f} — Thimi Investment"
        status_color = "#16a34a"
        status_title = "Loan Application Approved!"
        bg_color = "#f0fdf4"
        border_color = "#22c55e"
        msg_body = f"Congratulations! Your loan request of <strong>Rs. {loan.amount:,.2f}</strong> has been <strong>APPROVED</strong> and marked as Active."
    elif is_rejected:
        subject = f"❌ Loan Application Rejected: Rs. {loan.amount:,.2f} — Thimi Investment"
        status_color = "#dc2626"
        status_title = "Loan Application Rejected"
        bg_color = "#fef2f2"
        border_color = "#ef4444"
        msg_body = f"Your loan request of <strong>Rs. {loan.amount:,.2f}</strong> was <strong>REJECTED</strong> by administration."
    else:
        subject = f"ℹ️ Loan Status Updated ({status_str}): Rs. {loan.amount:,.2f} — Thimi Investment"
        status_color = "#2563eb"
        status_title = f"Loan Status Updated: {status_str}"
        bg_color = "#eff6ff"
        border_color = "#3b82f6"
        msg_body = f"The status of your loan (Rs. {loan.amount:,.2f}) has been updated to <strong>{status_str}</strong>."

    remarks_html = f"<p style='margin: 10px 0 0 0; font-size: 14px; color: #475569;'><strong>Remarks:</strong> {remarks or loan.remarks or 'Not specified'}</p>" if (remarks or loan.remarks) else ""

    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; background: #ffffff;">
        <div style="text-align: center; border-bottom: 2px solid {border_color}; padding-bottom: 16px; margin-bottom: 20px;">
            <h2 style="color: #1e293b; margin: 0;">Thimi Investment Group</h2>
            <p style="color: {status_color}; font-size: 15px; font-weight: bold; margin-top: 4px;">{status_title}</p>
        </div>

        <p style="font-size: 16px; color: #1e293b;">Dear <strong>{member_name}</strong>,</p>

        <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 16px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; font-size: 15px; color: #1e293b;">{msg_body}</p>
            {remarks_html}
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 6px; font-size: 14px; color: #475569;">
            <strong>Loan Details:</strong><br/>
            • Principal Amount: Rs. {loan.amount:,.2f}<br/>
            • Interest Rate: {float(loan.annual_interest_rate or 0)*100:.1f}% p.a.<br/>
            • Current Status: <strong style="color: {status_color};">{status_str.upper()}</strong>
        </div>

        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0 16px 0;" />
        <p style="font-size: 12px; color: #94a3b8; text-align: center; margin: 0;">
            Thimi Investment Group System Notification — Please do not reply directly to this email.
        </p>
    </div>
    """

    text_message = f"Dear {member_name}, your loan status for Rs. {loan.amount} has been updated to {status_str}."
    send_email_async(subject, text_message, [user_email], html_message)

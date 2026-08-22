import os
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
    """Sends email asynchronously, but falls back to synchronous if running in a CGI environment."""
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

    # CGI environments kill the process instantly on request completion.
    # If GATEWAY_INTERFACE is in os.environ, we must send synchronously.
    if 'GATEWAY_INTERFACE' in os.environ:
        _send()
    else:
        thread = threading.Thread(target=_send)
        thread.daemon = True
        thread.start()


# ─────────────────────────────────────────────────────────────────────────────
# SHARED EMAIL LAYOUT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _email_header(subtitle):
    return f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f1f5f9;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:32px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0;max-width:600px;">
      <tr>
        <td style="background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);padding:32px 40px;text-align:center;">
          <h1 style="color:#ffffff;margin:0;font-size:22px;font-weight:700;letter-spacing:0.5px;">Thimi Investment Group</h1>
          <p style="color:#bfdbfe;margin:6px 0 0 0;font-size:13px;letter-spacing:1px;text-transform:uppercase;">{subtitle}</p>
        </td>
      </tr>
      <tr><td style="padding:36px 40px;">"""


def _email_footer():
    return """      </td></tr>
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


def _detail_row(label, value, bg="#ffffff"):
    return f"""<tr style="background:{bg};">
  <td style="padding:11px 16px;font-size:13px;color:#64748b;border-bottom:1px solid #e2e8f0;width:40%;">{label}</td>
  <td style="padding:11px 16px;font-size:13px;color:#1e293b;font-weight:600;border-bottom:1px solid #e2e8f0;">{value}</td>
</tr>"""


def _cta_button(label, url):
    return f"""<div style="text-align:center;margin:28px 0 8px 0;">
  <a href="{url}" style="background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#ffffff;text-decoration:none;padding:14px 36px;font-size:15px;font-weight:700;border-radius:8px;display:inline-block;letter-spacing:0.3px;">
    {label}
  </a>
</div>"""


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

    # 1. Email to User — Claim Received Confirmation
    if user_email:
        user_subject = f"Payment Claim Received: Month {deposit.saving_month}/{deposit.saving_year} - Thimi Investment"
        user_html = (
            _email_header("Payment Claim Confirmation") +
            f"""
          <p style="font-size:16px;color:#1e293b;margin:0 0 6px 0;">Dear <strong>{member_name}</strong>,</p>
          <p style="font-size:14px;color:#64748b;margin:0 0 24px 0;">Member ID: <strong>{member_id}</strong></p>

          <div style="background:#f0fdf4;border:1px solid #22c55e;border-left:5px solid #22c55e;border-radius:8px;padding:16px 20px;margin-bottom:28px;">
            <p style="margin:0;font-size:15px;color:#15803d;font-weight:600;">
              Your payment claim has been successfully received.
            </p>
            <p style="margin:8px 0 0 0;font-size:14px;color:#166534;">
              It is currently <strong>Pending Verification</strong> by our admin team.
            </p>
          </div>

          <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:28px;">
            {_detail_row("Period", f"Month {deposit.saving_month}, {deposit.saving_year}", "#f8fafc")}
            {_detail_row("Amount Claimed", f"Rs. {deposit.amount:,.2f}")}
            {_detail_row("Payment Date", str(deposit.payment_date or "N/A"), "#f8fafc")}
            {_detail_row("Status", "Pending Verification")}
          </table>

          <p style="font-size:14px;color:#475569;margin:0 0 24px 0;">
            You will receive an email notification once your claim has been reviewed. Thank you for your prompt submission.
          </p>
          {_cta_button("View Dashboard", "https://www.thimiinvestment.com/")}
            """ +
            _email_footer()
        )
        user_text = f"Dear {member_name}, your payment claim of Rs. {deposit.amount} for Month {deposit.saving_month}/{deposit.saving_year} has been submitted and is pending verification."
        send_email_async(user_subject, user_text, [user_email], user_html)

    # 2. Email to Admin(s) — New Claim Alert
    admin_emails = get_admin_emails()
    if admin_emails:
        admin_subject = f"Admin Alert: New Payment Claim - {member_name} ({member_id})"
        admin_html = (
            _email_header("Admin Alert: New Payment Claim") +
            f"""
          <p style="font-size:15px;color:#1e293b;margin:0 0 24px 0;">
            A new payment claim has been submitted and requires your review.
          </p>

          <div style="background:#eff6ff;border:1px solid #93c5fd;border-left:5px solid #2563eb;border-radius:8px;padding:16px 20px;margin-bottom:28px;">
            <p style="margin:0;font-size:15px;color:#1e3a8a;font-weight:600;">New Payment Claim Received</p>
          </div>

          <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:28px;">
            {_detail_row("Member", member_name, "#f8fafc")}
            {_detail_row("Member ID", member_id)}
            {_detail_row("Period", f"Month {deposit.saving_month}, {deposit.saving_year}", "#f8fafc")}
            {_detail_row("Amount", f"Rs. {deposit.amount:,.2f}")}
            {_detail_row("Payment Date", str(deposit.payment_date or "N/A"), "#f8fafc")}
          </table>

          <p style="font-size:14px;color:#334155;margin:0 0 4px 0;">
            Please log into the Admin Dashboard to review and approve or reject this claim.
          </p>
          {_cta_button("Review in Admin Dashboard", "https://www.thimiinvestment.com/admin-dashboard/")}
            """ +
            _email_footer()
        )
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
    member_id = deposit.member.member_id
    is_approved = status_action.lower() == "approved"

    if is_approved:
        subject = f"Payment Claim Approved: Month {deposit.saving_month}/{deposit.saving_year} - Thimi Investment"
        status_color = "#16a34a"
        status_bg = "#f0fdf4"
        status_border = "#22c55e"
        banner_title = "Your Payment Claim Has Been Approved!"
        banner_body = f"Your payment of <strong>Rs. {deposit.amount:,.2f}</strong> for Month {deposit.saving_month}/{deposit.saving_year} has been <strong>approved</strong> and recorded."
        status_label = "Approved"
        follow_up = "Please log in to view your updated payment history."
    else:
        subject = f"Payment Claim Rejected: Month {deposit.saving_month}/{deposit.saving_year} - Thimi Investment"
        status_color = "#dc2626"
        status_bg = "#fef2f2"
        status_border = "#ef4444"
        banner_title = "Payment Claim Rejected"
        banner_body = f"Your payment claim of <strong>Rs. {deposit.amount:,.2f}</strong> for Month {deposit.saving_month}/{deposit.saving_year} has been <strong>rejected</strong> by the administrator."
        status_label = "Rejected"
        follow_up = "If you believe this is an error, please contact your group admin. You may re-submit your claim after clarifying."

    final_remarks = remarks or getattr(deposit, "remarks", None) or ""
    remarks_row = _detail_row("Remarks / Reason", final_remarks) if final_remarks else ""

    html_message = (
        _email_header("Payment Claim Status Update") +
        f"""
      <p style="font-size:16px;color:#1e293b;margin:0 0 6px 0;">Dear <strong>{member_name}</strong>,</p>
      <p style="font-size:14px;color:#64748b;margin:0 0 24px 0;">Member ID: <strong>{member_id}</strong></p>

      <div style="background:{status_bg};border:1px solid {status_border};border-left:5px solid {status_border};border-radius:8px;padding:18px 20px;margin-bottom:28px;">
        <p style="margin:0;font-size:16px;color:{status_color};font-weight:700;">{banner_title}</p>
        <p style="margin:10px 0 0 0;font-size:14px;color:#1e293b;">{banner_body}</p>
      </div>

      <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:28px;">
        {_detail_row("Period", f"Month {deposit.saving_month}, {deposit.saving_year}", "#f8fafc")}
        {_detail_row("Amount", f"Rs. {deposit.amount:,.2f}")}
        {_detail_row("Payment Date", str(deposit.payment_date or "N/A"), "#f8fafc")}
        {_detail_row("Final Status", f'<span style="color:{status_color};font-weight:700;">{status_label}</span>')}
        {remarks_row}
      </table>

      <p style="font-size:14px;color:#475569;margin:0 0 24px 0;">{follow_up}</p>
      {_cta_button("View My Dashboard", "https://www.thimiinvestment.com/")}
        """ +
        _email_footer()
    )

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

    # 1. Email to User — Loan Application Received
    if user_email:
        user_subject = f"Loan Application Received: Rs. {loan.amount:,.2f} - Thimi Investment"
        user_html = (
            _email_header("Loan Application Confirmation") +
            f"""
          <p style="font-size:16px;color:#1e293b;margin:0 0 24px 0;">Dear <strong>{member_name}</strong>,</p>

          <div style="background:#eff6ff;border:1px solid #93c5fd;border-left:5px solid #2563eb;border-radius:8px;padding:16px 20px;margin-bottom:28px;">
            <p style="margin:0;font-size:15px;color:#1e3a8a;font-weight:600;">Your Loan Application Has Been Received</p>
            <p style="margin:8px 0 0 0;font-size:14px;color:#1e40af;">
              Your application is currently <strong>under review</strong> by our administration team.
              You will be notified by email once a decision has been made.
            </p>
          </div>

          <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:28px;">
            {_detail_row("Requested Amount", f"Rs. {loan.amount:,.2f}", "#f8fafc")}
            {_detail_row("Annual Interest Rate", f"{float(loan.annual_interest_rate or 0)*100:.1f}% p.a.")}
            {_detail_row("Tenure", f"{loan.tenure_years or 0} year(s)", "#f8fafc")}
            {_detail_row("Purpose / Remarks", str(loan.remarks or "N/A"))}
            {_detail_row("Status", "Pending Review", "#f8fafc")}
          </table>

          <p style="font-size:14px;color:#475569;margin:0 0 24px 0;">
            You will receive an email update once your loan application decision has been finalized.
          </p>
          {_cta_button("View My Dashboard", "https://www.thimiinvestment.com/")}
            """ +
            _email_footer()
        )
        user_text = f"Dear {member_name}, your loan application of Rs. {loan.amount} has been received and is pending approval."
        send_email_async(user_subject, user_text, [user_email], user_html)

    # 2. Email to Admin(s) — New Loan Request Alert
    admin_emails = get_admin_emails()
    if admin_emails:
        admin_subject = f"Admin Alert: New Loan Application - {member_name} (Rs. {loan.amount:,.2f})"
        admin_html = (
            _email_header("Admin Alert: New Loan Request") +
            f"""
          <p style="font-size:15px;color:#1e293b;margin:0 0 24px 0;">
            A new loan application has been submitted and requires your review.
          </p>

          <div style="background:#eff6ff;border:1px solid #93c5fd;border-left:5px solid #2563eb;border-radius:8px;padding:16px 20px;margin-bottom:28px;">
            <p style="margin:0;font-size:15px;color:#1e3a8a;font-weight:600;">
              Loan Request: Rs. {loan.amount:,.2f}
            </p>
          </div>

          <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:28px;">
            {_detail_row("Applicant", member_name, "#f8fafc")}
            {_detail_row("Requested Amount", f"Rs. {loan.amount:,.2f}")}
            {_detail_row("Interest Rate", f"{float(loan.annual_interest_rate or 0)*100:.1f}% p.a.", "#f8fafc")}
            {_detail_row("Tenure", f"{loan.tenure_years or 0} year(s)")}
            {_detail_row("Purpose / Remarks", str(loan.remarks or "N/A"), "#f8fafc")}
          </table>

          <p style="font-size:14px;color:#334155;margin:0 0 4px 0;">
            Please log into the Admin Dashboard to review and take action on this loan request.
          </p>
          {_cta_button("Review in Admin Dashboard", "https://www.thimiinvestment.com/admin-dashboard/")}
            """ +
            _email_footer()
        )
        admin_text = f"Member {member_name} applied for a loan of Rs. {loan.amount}."
        send_email_async(admin_subject, admin_text, admin_emails, admin_html)


def send_loan_status_email(loan, status_action, remarks=None):
    """
    Triggers when an Admin updates loan status (Active/Approved or Rejected/Closed).
    Sends status notification email to member.
    """
    user_email = None
    member_name = loan.name or "Member"

    # Search User by name or username
    for u in User.objects.all():
        full = f"{u.first_name} {u.last_name}".strip()
        if (full and full.lower() == member_name.lower()) or u.username.lower() == member_name.lower():
            user_email = get_user_email(u)
            break

    if not user_email:
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
        subject = f"Loan Approved: Rs. {loan.amount:,.2f} - Thimi Investment"
        status_color = "#16a34a"
        status_bg = "#f0fdf4"
        status_border = "#22c55e"
        banner_title = "Your Loan Application Has Been Approved!"
        banner_body = f"Congratulations! Your loan of <strong>Rs. {loan.amount:,.2f}</strong> has been <strong>approved</strong> and marked as Active."
        status_label = "Approved / Active"
        follow_up = "Please log in to your dashboard to view your loan schedule and repayment details."
    elif is_rejected:
        subject = f"Loan Application Rejected: Rs. {loan.amount:,.2f} - Thimi Investment"
        status_color = "#dc2626"
        status_bg = "#fef2f2"
        status_border = "#ef4444"
        banner_title = "Loan Application Rejected"
        banner_body = f"Your loan request of <strong>Rs. {loan.amount:,.2f}</strong> has been <strong>rejected</strong> by the administration."
        status_label = "Rejected"
        follow_up = "If you have questions, please contact your group admin directly."
    else:
        subject = f"Loan Status Updated ({status_str}): Rs. {loan.amount:,.2f} - Thimi Investment"
        status_color = "#2563eb"
        status_bg = "#eff6ff"
        status_border = "#3b82f6"
        banner_title = f"Loan Status Updated to: {status_str}"
        banner_body = f"The status of your loan of <strong>Rs. {loan.amount:,.2f}</strong> has been updated to <strong>{status_str}</strong>."
        status_label = status_str.upper()
        follow_up = "Please log in to your dashboard for more details."

    final_remarks = remarks or getattr(loan, "remarks", None) or ""
    remarks_row = _detail_row("Remarks", final_remarks) if final_remarks else ""

    html_message = (
        _email_header("Loan Status Update") +
        f"""
      <p style="font-size:16px;color:#1e293b;margin:0 0 24px 0;">Dear <strong>{member_name}</strong>,</p>

      <div style="background:{status_bg};border:1px solid {status_border};border-left:5px solid {status_border};border-radius:8px;padding:18px 20px;margin-bottom:28px;">
        <p style="margin:0;font-size:16px;color:{status_color};font-weight:700;">{banner_title}</p>
        <p style="margin:10px 0 0 0;font-size:14px;color:#1e293b;">{banner_body}</p>
      </div>

      <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;margin-bottom:28px;">
        {_detail_row("Principal Amount", f"Rs. {loan.amount:,.2f}", "#f8fafc")}
        {_detail_row("Interest Rate", f"{float(loan.annual_interest_rate or 0)*100:.1f}% p.a.")}
        {_detail_row("Tenure", f"{loan.tenure_years or 0} year(s)", "#f8fafc")}
        {_detail_row("Final Status", f'<span style="color:{status_color};font-weight:700;">{status_label}</span>')}
        {remarks_row}
      </table>

      <p style="font-size:14px;color:#475569;margin:0 0 24px 0;">{follow_up}</p>
      {_cta_button("View My Dashboard", "https://www.thimiinvestment.com/")}
        """ +
        _email_footer()
    )

    text_message = f"Dear {member_name}, your loan status for Rs. {loan.amount} has been updated to {status_str}."
    send_email_async(subject, text_message, [user_email], html_message)



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
    """Sends email asynchronously, but falls back to synchronous if running in a CGI environment."""
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

    # CGI environments kill the process instantly on request completion.
    # If GATEWAY_INTERFACE is in os.environ, we must send synchronously.
    if 'GATEWAY_INTERFACE' in os.environ:
        _send()
    else:
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

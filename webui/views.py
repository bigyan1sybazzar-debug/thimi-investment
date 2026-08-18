from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from accounts.models import Member
from rest_framework_simplejwt.tokens import RefreshToken
import urllib.request
import urllib.parse
import urllib.error
import json

# ===========================
# Authentication
# ===========================

def login_view(request):
    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    return render(request, "login.html", {'google_client_id': google_client_id})

def google_callback_view(request):
    error = request.GET.get('error')

    if error:
        return HttpResponseRedirect(f"{reverse('login')}?error={error}")

    code = request.GET.get('code')
    if not code:
        return HttpResponseRedirect(f"{reverse('login')}?error=No OAuth code returned from Google.")

    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', '')

    if not client_id or not client_secret:
        return HttpResponseRedirect(f"{reverse('login')}?error=Google OAuth credentials are not configured on the server.")

    # Exchange authorization code for access/ID token
    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = request.build_absolute_uri(reverse('google_callback'))
    
    # Strip query parameters if redirect_uri had any
    if '?' in redirect_uri:
        redirect_uri = redirect_uri.split('?')[0]

    post_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    try:
        req_data = urllib.parse.urlencode(post_data).encode('utf-8')
        token_req = urllib.request.Request(token_url, data=req_data, method='POST')
        
        try:
            with urllib.request.urlopen(token_req, timeout=10) as resp:
                token_json = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            err_json = json.loads(e.read().decode('utf-8'))
            error_msg = err_json.get('error_description', 'Token exchange failed.')
            return HttpResponseRedirect(f"{reverse('login')}?error={error_msg}")

        # Verify the ID Token with Google tokeninfo endpoint
        id_token = token_json.get('id_token')
        if not id_token:
            return HttpResponseRedirect(f"{reverse('login')}?error=No ID Token returned from Google.")

        info_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        info_req = urllib.request.Request(info_url, method='GET')
        
        try:
            with urllib.request.urlopen(info_req, timeout=10) as resp:
                info_json = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            err_json = json.loads(e.read().decode('utf-8'))
            error_msg = err_json.get('error_description', 'Failed to verify token identity.')
            return HttpResponseRedirect(f"{reverse('login')}?error={error_msg}")

        email = info_json.get('email')
        if not email:
            return HttpResponseRedirect(f"{reverse('login')}?error=Email address not provided by Google.")

    except Exception as e:
        return HttpResponseRedirect(f"{reverse('login')}?error=Failed to connect to Google validation service: {str(e)}")

    # Find or check User
    try:
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            # Fallback check on username field
            user = User.objects.filter(username__iexact=email).first()
            
        if not user:
            return HttpResponseRedirect(f"{reverse('login')}?error=This Google account is not registered. Access denied.")
        
        # Generate SimpleJWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Get role details to redirect to the correct dashboard page
        is_staff = user.is_staff or user.is_superuser

        redirect_path = "/member/dashboard/"
        if is_staff:
            redirect_path = "/admin-dashboard/"

        # Render a simple HTML page that writes tokens to localStorage and redirects the browser
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Sign-in Redirecting...</title>
        </head>
        <body>
            <p>Signing in, redirecting...</p>
            <script>
                localStorage.setItem("access", "{access_token}");
                localStorage.setItem("refresh", "{refresh_token}");
                window.location.href = "{redirect_path}";
            </script>
        </body>
        </html>
        """
        return HttpResponse(html_content)

    except Exception as e:
        return HttpResponseRedirect(f"{reverse('login')}?error=Failed to login: {str(e)}")


# ===========================
# Member
# ===========================

def member_dashboard(request):
    return render(request, "member/dashboard.html")


def claim_payment(request):
    return render(request, "member/claim_payment.html")


# ===========================
# Admin
# ===========================

def admin_dashboard(request):
    return render(request, "admin/dashboard.html")


def members(request):
    return render(request, "admin/members.html")


def member_list(request):
    return render(request, "admin/members/member_list.html")


def add_member(request):
    return render(request, "admin/members/add_member.html")


def edit_member(request, id):
    return render(
        request,
        "admin/members/edit_member.html",
        {"id": id},
    )


def member_profile(request, id):
    return render(
        request,
        "admin/members/member_profile.html",
        {"id": id},
    )


def deposits_view(request):
    return render(request, "admin/deposits.html")


def loans_view(request):
    return render(request, "admin/loans.html")


def investments_view(request):
    return render(request, "admin/investments.html")


def reports_view(request):
    return render(request, "admin/reports.html")


def notifications_view(request):
    return render(request, "admin/notifications.html")


def settings_view(request):
    return render(request, "admin/settings.html")


def expenses_view(request):
    return render(request, "admin/expenses.html")
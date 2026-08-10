from django.shortcuts import render


# ===========================
# Authentication
# ===========================

def login_view(request):
    return render(request, "login.html")


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
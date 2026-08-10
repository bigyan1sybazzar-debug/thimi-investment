from django.urls import path
from . import views

urlpatterns = [

    # ==========================
    # Authentication
    # ==========================
    path("", views.login_view, name="login"),

    # ==========================
    # Member
    # ==========================
    path("member/dashboard/", views.member_dashboard, name="member_dashboard"),
    path("member/claim-payment/", views.claim_payment, name="claim_payment"),

    # ==========================
    # Admin Dashboard
    # ==========================
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # ==========================
    # Member Management
    # ==========================
    path("members/", views.member_list, name="member_list"),
    path("members/add/", views.add_member, name="add_member"),
    path("members/edit/<int:id>/", views.edit_member, name="edit_member"),
    path("members/profile/<int:id>/", views.member_profile, name="member_profile"),

    # ==========================
    # Admin Sidebar Pages
    # ==========================
    path("deposits/", views.deposits_view, name="admin_deposits"),
    path("loans/", views.loans_view, name="admin_loans"),
    path("investments/", views.investments_view, name="admin_investments"),
    path("reports/", views.reports_view, name="admin_reports"),
    path("notifications/", views.notifications_view, name="admin_notifications"),
    path("settings/", views.settings_view, name="admin_settings"),
]
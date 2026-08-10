from django.urls import path

from .views import (
    DepositListCreateView,
    MemberDashboardAPI,
    AdminDepositListView,
    AdminDepositDetailView,
    ApproveDepositView,
    RejectDepositView,
    AdminDashboardAPI,
    GlobalSettingAPI,
)

urlpatterns = [
    # Global configurations
    path(
        "settings/",
        GlobalSettingAPI.as_view(),
        name="global-settings",
    ),

    # ============================
    # Member APIs
    # ============================
    path(
        "",
        DepositListCreateView.as_view(),
        name="deposit-list-create",
    ),

    path(
        "dashboard/",
        MemberDashboardAPI.as_view(),
        name="member-dashboard",
    ),

    # ============================
    # Admin APIs
    # ============================
    path(
        "admin/dashboard/",
        AdminDashboardAPI.as_view(),
        name="admin-dashboard",
    ),

    path(
        "admin/deposits/",
        AdminDepositListView.as_view(),
        name="admin-deposit-list",
    ),

    path(
        "admin/deposits/<int:pk>/",
        AdminDepositDetailView.as_view(),
        name="admin-deposit-detail",
    ),

    path(
        "admin/deposits/<int:pk>/approve/",
        ApproveDepositView.as_view(),
        name="approve-deposit",
    ),

    path(
        "admin/deposits/<int:pk>/reject/",
        RejectDepositView.as_view(),
        name="reject-deposit",
    ),
]
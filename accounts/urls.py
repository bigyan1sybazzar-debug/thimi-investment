from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView,
    CurrentUserView,
    MemberSelfUpdateProfileView,
    RelatedDocumentListView,
    RelatedDocumentManageView,
)

urlpatterns = [

    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "login/",
        TokenObtainPairView.as_view(),
        name="login",
    ),

    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="refresh",
    ),

    path(
        "me/",
        CurrentUserView.as_view(),
        name="current-user",
    ),

    path(
        "update-profile/",
        MemberSelfUpdateProfileView.as_view(),
        name="update-profile",
    ),

    path(
        "documents/",
        RelatedDocumentListView.as_view(),
        name="footer-documents",
    ),

    path(
        "documents/manage/",
        RelatedDocumentManageView.as_view(),
        name="manage-documents",
    ),

]
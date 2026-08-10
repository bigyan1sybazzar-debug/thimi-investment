from django.urls import path

from .views import (
    MemberListView,
    MemberDetailView,
    MemberUpdateView,
)

urlpatterns = [

    path(
        "",
        MemberListView.as_view(),
    ),

    path(
        "<int:pk>/",
        MemberDetailView.as_view(),
    ),
    path(
    "<int:pk>/update/",
    MemberUpdateView.as_view(),
),

]
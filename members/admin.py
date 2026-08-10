from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "member_id",
        "full_name",
        "phone",
        "status",
        "joined_date",
    )

    list_filter = (
        "status",
        "joined_date",
    )

    search_fields = (
        "member_id",
        "full_name",
        "phone",
    )
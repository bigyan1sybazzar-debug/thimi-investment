from rest_framework import serializers
from accounts.models import Member


class MemberSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Member
        fields = [
            "id",
            "member_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "address",
            "join_date",
            "is_active_member",
            "remaining_days",
            "remaining_days_updated_at",
        ]
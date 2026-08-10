from rest_framework import serializers
from .models import Deposit


class AdminDepositSerializer(serializers.ModelSerializer):

    member_name = serializers.CharField(
        source="member.user.username",
        read_only=True
    )

    member_id = serializers.CharField(
        source="member.member_id",
        read_only=True
    )

    screenshot_url = serializers.SerializerMethodField()

    class Meta:
        model = Deposit
        fields = [
            "id",
            "member_name",
            "member_id",
            "amount",
            "saving_year",
            "saving_month",
            "payment_date",
            "payment_method",
            "status",
            "remarks",
            "created_at",
            "screenshot_url",
        ]
        read_only_fields = [
            "id",
            "member_name",
            "member_id",
            "created_at",
            "screenshot_url",
        ]

    def get_screenshot_url(self, obj):
        request = self.context.get("request")
        if obj.screenshot and request:
            return request.build_absolute_uri(obj.screenshot.url)
        return None
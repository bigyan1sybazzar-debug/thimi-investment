from rest_framework import serializers
from .models import Deposit


class DepositSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deposit
        fields = "__all__"

        read_only_fields = (
            "member",
            "status",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        )

    def validate_saving_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError(
                "Saving month must be between 1 and 12."
            )
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than zero."
            )
        return value
from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    added_by_name = serializers.SerializerMethodField()
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id", "title", "amount", "category", "date",
            "description", "receipt", "receipt_url",
            "added_by", "added_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ("added_by", "created_at", "updated_at")

    def get_added_by_name(self, obj):
        if obj.added_by:
            name = f"{obj.added_by.first_name} {obj.added_by.last_name}".strip()
            return name or obj.added_by.username
        return None

    def get_receipt_url(self, obj):
        if obj.receipt:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.receipt.url)
            return obj.receipt.url
        return None

from rest_framework import serializers
from .models import StockTransaction, ShareInventory


class StockTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransaction
        fields = "__all__"


class ShareInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareInventory
        fields = "__all__"

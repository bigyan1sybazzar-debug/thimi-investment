from rest_framework import serializers
from .models import Loan


class LoanSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    disbursement_date = serializers.DateField(required=False)

    class Meta:
        model = Loan
        fields = "__all__"


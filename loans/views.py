from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Loan
from .serializers import LoanSerializer


class LoanListCreateView(generics.ListCreateAPIView):
    """GET = all users can view. POST = admin only."""
    serializer_class = LoanSerializer

    def get_queryset(self):
        if not Loan.objects.exists():
            default_loans = [
                Loan(name="Atlantic Bhandari", amount=200000, disbursement_date="2025-09-01", status="Closed", interest_paid=12000),
                Loan(name="Dipin Gyawali", amount=200000, disbursement_date="2025-11-30", status="Closed", interest_paid=12000),
                Loan(name="Pawan Gyawali", amount=200000, disbursement_date="2025-12-01", status="Closed", interest_paid=12000),
                Loan(name="Devendra Sharma", amount=100000, disbursement_date="2025-03-22", status="Active", interest_paid=2000),
            ]
            Loan.objects.bulk_create(default_loans)
        return Loan.objects.all()

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        from django.utils import timezone
        kwargs = {}
        if not serializer.validated_data.get('name'):
            name = f"{self.request.user.first_name} {self.request.user.last_name}".strip() or self.request.user.username
            kwargs['name'] = name
        if not serializer.validated_data.get('disbursement_date'):
            kwargs['disbursement_date'] = timezone.now().date()
        if not self.request.user.is_staff:
            kwargs['status'] = "Pending"
            kwargs['interest_paid'] = 0

        serializer.save(**kwargs)



class LoanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET = all authenticated. PUT/PATCH/DELETE = admin only."""
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

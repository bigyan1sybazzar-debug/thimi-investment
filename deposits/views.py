from django.db.models import Sum
from django.utils import timezone

from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Member, GlobalSetting
from .models import Deposit
from .serializers import DepositSerializer
from .admin_serializers import AdminDepositSerializer
from notifications_app.email_utils import (
    send_deposit_claimed_emails,
    send_deposit_status_email,
)



THIMI_DATA = {
    "workbook": "Thimi Investment",
    "currency": "NPR",
    "bank_and_deposit_summary": {
        "cash_at_bank": {
            "Pradeep": None,
            "Pawan": 1182774.0
        },
        "total_shown": 1769325,
        "note": "Pradeep cash-at-bank amount is marked 'Please update' in the source."
    },
    "loans": {
        "annual_interest_rate": 0.12,
        "tenure_years": 0.5,
        "records": [
            {
                "s_no": 1,
                "name": "Atlantic Bhandari",
                "amount": 200000,
                "disbursement_date": "2025/09/01",
                "status": "Closed",
                "interest_paid": 12000
            },
            {
                "s_no": 2,
                "name": "Dipin Gyawali",
                "amount": 200000,
                "disbursement_date": "2025/11/30",
                "status": "Closed",
                "interest_paid": 12000
            },
            {
                "s_no": 3,
                "name": "Pawan Gyawali",
                "amount": 200000,
                "disbursement_date": "2025/12/01",
                "status": "Closed",
                "interest_paid": 12000
            },
            {
                "s_no": 4,
                "name": "Devendra Sharma",
                "amount": 100000,
                "disbursement_date": "2025/03/22",
                "status": "Active",
                "interest_paid": 2000
            }
        ],
        "total_principal": 700000,
        "total_interest_paid": 38000
    },
    "loan_interest_payments": {
        "rate": "12% p.a.",
        "payments": [
            {
                "name": "Atlantic Bhandari",
                "amount": 2000,
                "status": "Cleared"
            },
            {
                "name": "Dipin Gyawali",
                "amount": 2000,
                "status": "Cleared"
            },
            {
                "name": "Pawan Gyawali",
                "amount": 2000,
                "status": "Cleared"
            },
            {
                "name": "Devendra Sharma",
                "amount": 1000,
                "status": "Active"
            }
        ],
        "total": 7000
    },
    "financial_summary": {
        "final_till_2025_end": 98107.35,
        "total_cash": 108507.35,
        "total_amount_collected": 1358015,
        "pradeep_bank_plus_share_profit": 543124.5,
        "pawan_bank_total_collected": 828414.55,
        "amount_and_share_description_to_be_shared_by_pradeep_tandan": 2487.8,
        "total_amount_invested_on_shares": 540656.7,
        "share_value": 507493.4,
        "share_value_breakdown": "271293.4 + 197600 + 38600",
        "loan": 600000,
        "pawan_summary": {
            "to_be_collected": 828414.55,
            "loans": 600000,
            "collateral_shares": 114000,
            "repayment": 8395,
            "cash_remaining_in_bank": 106019.55
        },
        "fine_and_payment": {
            "person": "Bikalpa Khadka",
            "monthly_addition": "21600 + 8395",
            "total": 29995
        }
    },
    "share_details": {
        "shares_in_stock": [
            {
                "stock": "SONA",
                "no_of_kitta": 880
            },
            {
                "stock": "NIMB",
                "no_of_kitta": 200
            }
        ],
        "pradeep_account": [
            {
                "stock": "SONA",
                "cost": 377784,
                "note": "LTP as of Asar 4th"
            },
            {
                "stock": "NIMB",
                "cost": 39040,
                "note": "LTP as of Asar 4th"
            }
        ],
        "pradeep_total_cost": 416824,
        "sandesh_account": {
            "stock": None,
            "cost": 0
        },
        "total": 416824
    },
    "hydropower_plan": {
        "price_per_unit": 70,
        "status_note": "Dismissed Plan",
        "deposits": [
            {
                "name": "Bikalpa",
                "amount": None
            },
            {
                "name": "Sandesh",
                "amount": None
            },
            {
                "name": "Prabin",
                "amount": None
            },
            {
                "name": "Prashant",
                "amount": 60000
            },
            {
                "name": "Pradeep",
                "amount": None
            },
            {
                "name": "Yuben",
                "amount": 60000
            },
            {
                "name": "Dipin",
                "amount": 60000
            }
        ],
        "total": 180000
    },
    "stock_transactions": {
        "ltp_date": "06/05/2026",
        "transactions": [
            {
                "s_no": 1,
                "date": "18/4/2081",
                "symbol": "RIDI",
                "shares": 295,
                "buying_price": 252.5024,
                "buy_amount_with_tax": 74488.208,
                "selling_price": 287,
                "sell_amount_after_tax": 84372.94,
                "profit_loss": 9884.732,
                "status": "Sold"
            },
            {
                "s_no": 2,
                "date": "29/4/2081",
                "symbol": "UMHL",
                "shares": 215,
                "buying_price": 354,
                "buy_amount_with_tax": 76372.58,
                "status": "Holding",
                "remarks": "Pradeep"
            },
            {
                "s_no": 2,
                "date": "29/4/2081",
                "symbol": "MHNL",
                "shares": 200,
                "buying_price": 386.59,
                "buy_amount_with_tax": 77320,
                "status": "Holding",
                "remarks": "Sandesh"
            },
            {
                "s_no": 3,
                "date": "29/8/2081",
                "symbol": "PRVU",
                "shares": 577,
                "buying_price": 251.5,
                "buy_amount_with_tax": 145115.5,
                "status": "Holding",
                "remarks": "Pradeep"
            },
            {
                "s_no": 3,
                "date": "15/9/2081",
                "symbol": "MHNL",
                "shares": 760,
                "buying_price": 280.87,
                "buy_amount_with_tax": 213461.2,
                "status": "Holding"
            },
            {
                "s_no": 3,
                "date": "23/9/2081",
                "symbol": "PRVU",
                "shares": 80,
                "buying_price": 235,
                "buy_amount_with_tax": 18800,
                "status": "Holding",
                "remarks": "Pradeep"
            },
            {
                "date": "18/10/2081",
                "symbol": "UMHL",
                "shares": 215,
                "selling_price": 388,
                "sell_amount_after_tax": 83472.58,
                "profit_loss": 7100,
                "status": "Sold",
                "remarks": "Pradeep"
            },
            {
                "date": "16/10/2081",
                "symbol": "MHNL",
                "shares": 300,
                "buying_price": 271,
                "buy_amount_with_tax": 81300,
                "status": "Holding",
                "remarks": "Pradeep"
            },
            {
                "date": "24/11/2081",
                "symbol": "MHNL",
                "shares": 400,
                "selling_price": 274,
                "sell_amount_after_tax": 128040.09,
                "profit_loss": -3180.2,
                "status": "Sold",
                "remarks": "Pradeep"
            },
            {
                "date": "24/11/2081",
                "symbol": "PRVU",
                "shares": 600,
                "buying_price": 224.5,
                "buy_amount_with_tax": 134700,
                "status": "Holding",
                "remarks": "Pradeep"
            },
            {
                "date": "13/07/2025",
                "symbol": "SANIMA",
                "shares": 400,
                "buying_price": 597.3,
                "buy_amount_with_tax": 59705.28,
                "selling_price": 685.3,
                "sell_amount_after_tax": 67863.2,
                "profit_loss": 8147.92,
                "status": "Sold",
                "remarks": "Pawan"
            },
            {
                "date": "14/07/2025",
                "symbol": "DELTI",
                "shares": 400,
                "buying_price": 567.19,
                "buy_amount_with_tax": 56804.09,
                "selling_price": 626.05,
                "sell_amount_after_tax": 62092.8,
                "profit_loss": 5297.97,
                "status": "Sold",
                "remarks": "Pawan"
            },
            {
                "date": "16/07/2025",
                "symbol": "SANIMA",
                "shares": 400,
                "buying_price": 386.64,
                "buy_amount_with_tax": 38638.88,
                "selling_price": 377,
                "sell_amount_after_tax": 37498.12,
                "profit_loss": -1140.76,
                "status": "Sold",
                "remarks": "Pawan"
            },
            {
                "date": "29/07/2025",
                "symbol": "NIMB",
                "shares": 200,
                "buying_price": 243.9,
                "buy_amount_with_tax": 48780,
                "ltp": 197.3,
                "ltp_value": 39460,
                "status": "Holding",
                "remarks": "Pawan"
            },
            {
                "date": "29/07/2025",
                "symbol": "PRVU",
                "shares": 200,
                "buying_price": 246.5,
                "buy_amount_with_tax": 49300,
                "selling_price": 185.1,
                "status": "Loss",
                "remarks": "Pawan"
            }
        ],
        "share_inventory": [
            {
                "stock": "UMHL",
                "no_of_kitta": 215
            },
            {
                "stock": "MHNL",
                "no_of_kitta": 580
            },
            {
                "stock": "PRVU",
                "no_of_kitta": 1377
            },
            {
                "stock": "NIMB",
                "no_of_kitta": 200
            }
        ],
        "pradeep_sold": [
            {
                "stock": "MHNL",
                "shares": 600,
                "cost": 168721.2,
                "sold": 146400
            },
            {
                "stock": "PRVU",
                "shares": 1257,
                "cost": 298615.5,
                "sold": 233802
            }
        ],
        "pradeep_sold_total": {
            "cost": 467336.7,
            "sold": 380202
        },
        "sandesh_sold": {
            "stock": "MHNL",
            "shares": 200,
            "cost": 73320,
            "sold": 48560,
            "loss": 24760
        },
        "active_pradeep": {
            "stock": "SONA",
            "shares": 800,
            "sold_value": 374968,
            "note": "as of Asar 6th"
        },
        "total_loss_in_shares_till_date": 117128.7
    }
}

# =====================================================
# MEMBER - Deposit List & Create (Claim Payment)
# =====================================================
class DepositListCreateView(generics.ListCreateAPIView):

    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        member = Member.objects.get(user=self.request.user)
        return Deposit.objects.filter(member=member).order_by("-created_at")

    def perform_create(self, serializer):

        member = Member.objects.get(user=self.request.user)

        saving_year = serializer.validated_data["saving_year"]
        saving_month = serializer.validated_data["saving_month"]

        # Prevent duplicate monthly claim unless previous claim was rejected
        existing = Deposit.objects.filter(
            member=member,
            saving_year=saving_year,
            saving_month=saving_month
        ).first()

        if existing:
            if existing.status == "rejected":
                existing.delete()
            else:
                raise serializers.ValidationError(
                    {
                        "detail": "You have already submitted a payment claim for this month."
                    }
                )

        deposit = serializer.save(
            member=member,
            status="pending"
        )

        send_deposit_claimed_emails(deposit)


# =====================================================
# MEMBER DASHBOARD
# =====================================================
class MemberDashboardAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        member = Member.objects.get(user=request.user)
        global_setting, _ = GlobalSetting.objects.get_or_create(id=1)

        deposits = Deposit.objects.filter(member=member)

        total = deposits.aggregate(
            total=Sum("amount")
        )["total"] or 0

        pending = deposits.filter(
            status="pending"
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        approved = deposits.filter(
            status="approved"
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        rejected = deposits.filter(
            status="rejected"
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        data = {
            "member": {
                "username": member.user.username,
                "first_name": member.user.first_name,
                "last_name": member.user.last_name,
                "member_id": member.member_id,
                "phone": member.phone,
                "address": member.address,
                "is_staff": member.user.is_staff,
                "is_superuser": member.user.is_superuser,
                "remaining_days": global_setting.remaining_days,
                "remaining_days_updated_at": global_setting.remaining_days_updated_at,
                "gov_id_front": request.build_absolute_uri(member.gov_id_front.url) if member.gov_id_front else None,
                "gov_id_back": request.build_absolute_uri(member.gov_id_back.url) if member.gov_id_back else None,
            },
            "summary": {
                "total_deposit": total,
                "approved_deposit": approved,
                "pending_deposit": pending,
                "rejected_deposit": rejected,
            },
            "deposits": DepositSerializer(
                deposits.order_by("-created_at"),
                many=True
            ).data,
            "thimi_data": THIMI_DATA,
        }

        return Response(data)


# =====================================================
# ADMIN - Deposit List
# =====================================================
class AdminDepositListView(generics.ListAPIView):

    serializer_class = AdminDepositSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):

        queryset = Deposit.objects.select_related(
            "member",
            "member__user"
        ).order_by("-created_at")

        status_param = self.request.GET.get("status")
        month = self.request.GET.get("month")
        year = self.request.GET.get("year")
        search = self.request.GET.get("search")

        if status_param:
            queryset = queryset.filter(status=status_param)

        if month:
            queryset = queryset.filter(saving_month=month)

        if year:
            queryset = queryset.filter(saving_year=year)

        if search:
            queryset = queryset.filter(
                member__user__username__icontains=search
            )

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


# =====================================================
# ADMIN - Deposit Detail / Edit / Delete
# =====================================================
class AdminDepositDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Deposit.objects.all()
    serializer_class = AdminDepositSerializer
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        response = self.update(request, *args, **kwargs)
        if response.status_code in (200, 201):
            deposit = self.get_object()
            if "status" in request.data:
                send_deposit_status_email(deposit, deposit.status, remarks=request.data.get("remarks"))
        return response


# =====================================================
# ADMIN - Approve Deposit
# =====================================================
class ApproveDepositView(APIView):

    permission_classes = [IsAdminUser]

    def put(self, request, pk):

        try:
            deposit = Deposit.objects.get(pk=pk)

        except Deposit.DoesNotExist:
            return Response(
                {"detail": "Deposit not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        deposit.status = "approved"
        deposit.approved_by = request.user
        deposit.approved_at = timezone.now()
        deposit.save()

        send_deposit_status_email(deposit, "approved")

        return Response(
            {
                "message": "Deposit approved successfully.",
                "status": deposit.status,
            }
        )


# =====================================================
# ADMIN - Reject Deposit
# =====================================================
class RejectDepositView(APIView):

    permission_classes = [IsAdminUser]

    def put(self, request, pk):

        try:
            deposit = Deposit.objects.get(pk=pk)

        except Deposit.DoesNotExist:
            return Response(
                {"detail": "Deposit not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        deposit.status = "rejected"
        deposit.approved_by = request.user
        deposit.approved_at = timezone.now()
        deposit.save()

        send_deposit_status_email(deposit, "rejected")

        return Response(
            {
                "message": "Deposit rejected successfully.",
                "status": deposit.status,
            }
        )


# =====================================================
# ADMIN DASHBOARD
# =====================================================
class AdminDashboardAPI(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        total_members = Member.objects.count()

        active_members = Member.objects.filter(
            is_active_member=True
        ).count()

        pending = Deposit.objects.filter(
            status="pending"
        ).count()

        approved = Deposit.objects.filter(
            status="approved"
        ).count()

        rejected = Deposit.objects.filter(
            status="rejected"
        ).count()

        total_collection = Deposit.objects.filter(
            status="approved"
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        return Response(
            {
                "total_members": total_members,
                "active_members": active_members,
                "pending_deposits": pending,
                "approved_deposits": approved,
                "rejected_deposits": rejected,
                "total_collection": total_collection,
                "thimi_data": THIMI_DATA,
            }
        )


# =====================================================
# GLOBAL CONFIG / DEADLINE SETTING
# =====================================================
class GlobalSettingAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        setting, _ = GlobalSetting.objects.get_or_create(id=1)
        qr_url = None
        if setting.qr_code:
            qr_url = request.build_absolute_uri(setting.qr_code.url)
        return Response({
            "remaining_days": setting.remaining_days,
            "remaining_days_updated_at": setting.remaining_days_updated_at,
            "qr_code_url": qr_url,
        })

    def post(self, request):
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        setting, _ = GlobalSetting.objects.get_or_create(id=1)

        remaining_days = request.data.get("remaining_days")
        if remaining_days is not None:
            try:
                setting.remaining_days = int(remaining_days)
            except ValueError:
                return Response(
                    {"detail": "Invalid remaining_days value."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        qr_file = request.FILES.get("qr_code")
        if qr_file:
            setting.qr_code = qr_file

        setting.save()

        qr_url = None
        if setting.qr_code:
            qr_url = request.build_absolute_uri(setting.qr_code.url)

        return Response({
            "remaining_days": setting.remaining_days,
            "remaining_days_updated_at": setting.remaining_days_updated_at,
            "qr_code_url": qr_url,
            "message": "Settings updated successfully."
        })
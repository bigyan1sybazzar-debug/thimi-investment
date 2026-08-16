from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Member
from .serializers import MemberSerializer


# ==========================================
# List All Members
# ==========================================
class MemberListView(generics.ListAPIView):

    queryset = Member.objects.all().order_by("member_id")

    serializer_class = MemberSerializer

    permission_classes = [IsAdminUser]


# ==========================================
# Member Detail
# ==========================================
class MemberDetailView(generics.RetrieveAPIView):

    queryset = Member.objects.all()

    serializer_class = MemberSerializer

    permission_classes = [IsAdminUser]

class MemberUpdateView(generics.UpdateAPIView):

    queryset = Member.objects.all()

    serializer_class = MemberSerializer

    permission_classes = [IsAdminUser]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# ==========================================
# Admin: Full User + Member Update
# ==========================================
class MemberAdminUpdateView(APIView):
    """
    PATCH /api/members/<pk>/admin-update/
    Allows staff/superusers to change:
      - email, password, first_name, last_name  (on the User object)
      - is_staff (promote/demote admin)
      - phone, address, is_active_member         (on the Member object)
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return Response({"detail": "Member not found."}, status=status.HTTP_404_NOT_FOUND)

        user = member.user

        # --- User-level fields ---
        email = request.data.get("email")
        if email:
            user.email = email

        password = request.data.get("password")
        if password:
            user.set_password(password)

        first_name = request.data.get("first_name")
        if first_name is not None:
            user.first_name = first_name

        last_name = request.data.get("last_name")
        if last_name is not None:
            user.last_name = last_name

        is_staff = request.data.get("is_staff")
        if is_staff is not None:
            user.is_staff = str(is_staff).lower() in ("true", "1", "yes")

        user.save()

        # --- Member-level fields ---
        phone = request.data.get("phone")
        if phone is not None:
            member.phone = phone

        address = request.data.get("address")
        if address is not None:
            member.address = address

        is_active = request.data.get("is_active_member")
        if is_active is not None:
            member.is_active_member = str(is_active).lower() in ("true", "1", "yes")

        if request.FILES.get("gov_id_front"):
            member.gov_id_front = request.FILES.get("gov_id_front")
        if request.FILES.get("gov_id_back"):
            member.gov_id_back = request.FILES.get("gov_id_back")

        member.save()

        return Response({
            "message": "Member updated successfully.",
            "member_id": member.member_id,
            "email": user.email,
            "is_staff": user.is_staff,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": member.phone,
            "address": member.address,
            "is_active_member": member.is_active_member,
            "gov_id_front": request.build_absolute_uri(member.gov_id_front.url) if member.gov_id_front else None,
            "gov_id_back": request.build_absolute_uri(member.gov_id_back.url) if member.gov_id_back else None,
        })
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

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
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Member, RelatedDocument
from notifications_app.models import SystemNotification


class RegisterView(APIView):

    def post(self, request):

        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        return Response(
            {
                "message": "User created successfully",
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )


class CurrentUserView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_member": False,
            "member_id": None,
        }

        try:
            member = Member.objects.get(user=user)

            data["is_member"] = True
            data["member_id"] = member.member_id

        except Member.DoesNotExist:
            pass

        return Response(data)


class MemberSelfUpdateProfileView(APIView):
    """
    POST /api/accounts/update-profile/
    Allows logged-in member to update their email address and/or change password.
    Creates a SystemNotification so admins can see user setting changes.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        email = (request.data.get("email") or "").strip()
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        changes = []

        # Password Change Logic
        if new_password:
            if not current_password:
                return Response(
                    {"detail": "Current password is required to set a new password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not user.check_password(current_password):
                return Response(
                    {"detail": "Incorrect current password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if len(new_password) < 8:
                return Response(
                    {"detail": "New password must be at least 8 characters long."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            changes.append("Password changed successfully")

        # Email Change Logic
        if email and email != user.email:
            if "@" not in email:
                return Response(
                    {"detail": "Invalid email address format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            old_email = user.email or user.username
            user.email = email
            user.username = email
            changes.append(f"Email changed from '{old_email}' to '{email}'")

        # Government ID Upload Logic
        gov_id_front = request.FILES.get("gov_id_front")
        gov_id_back = request.FILES.get("gov_id_back")

        try:
            member = Member.objects.get(user=user)
            member_updated = False
            if gov_id_front:
                member.gov_id_front = gov_id_front
                changes.append("Uploaded Government ID Front image")
                member_updated = True
            if gov_id_back:
                member.gov_id_back = gov_id_back
                changes.append("Uploaded Government ID Back image")
                member_updated = True
            if member_updated:
                member.save()
        except Member.DoesNotExist:
            pass

        if not changes:
            return Response(
                {"detail": "No profile changes were submitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.save()

        # Send System Notification / Message to Admin
        member_id = getattr(getattr(user, "member_profile", None), "member_id", user.username)
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        change_summary = "; ".join(changes)

        SystemNotification.objects.create(
            user=user,
            title=f"Member Profile Update ({member_id})",
            message=f"Member {full_name} (ID: {member_id}) updated settings: {change_summary}.",
            category="profile_update",
        )

        return Response(
            {
                "message": "Profile settings updated successfully.",
                "email": user.email,
                "username": user.username,
                "changes": changes,
            }
        )


class RelatedDocumentListView(APIView):
    """
    GET /api/accounts/documents/
    Returns active related documents for display in footer.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        docs = RelatedDocument.objects.filter(is_active=True).order_by("-uploaded_at")
        data = []
        for d in docs:
            data.append({
                "id": d.id,
                "title": d.title,
                "description": d.description or "",
                "file_url": d.file.url if d.file else "",
                "uploaded_at": d.uploaded_at.strftime("%Y-%m-%d"),
            })
        return Response(data)


class RelatedDocumentManageView(APIView):
    """
    POST /api/accounts/documents/manage/ (Upload)
    DELETE /api/accounts/documents/manage/?id=<id> (Delete)
    Allows admin to upload and delete related footer documents.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description", "")
        file_obj = request.FILES.get("file")

        if not title or not file_obj:
            return Response(
                {"detail": "Title and file are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        doc = RelatedDocument.objects.create(
            title=title,
            description=description,
            file=file_obj,
            is_active=True,
        )

        return Response(
            {
                "message": "Document uploaded successfully.",
                "id": doc.id,
                "title": doc.title,
                "file_url": doc.file.url if doc.file else "",
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request):
        doc_id = request.query_params.get("id")
        if not doc_id:
            return Response({"detail": "Document ID required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doc = RelatedDocument.objects.get(id=doc_id)
            doc.delete()
            return Response({"message": "Document deleted successfully."})
        except RelatedDocument.DoesNotExist:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
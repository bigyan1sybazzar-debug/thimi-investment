from rest_framework import serializers
from accounts.models import Member


class MemberSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    is_staff = serializers.BooleanField(source="user.is_staff", read_only=True)
    gov_id_front = serializers.SerializerMethodField()
    gov_id_back = serializers.SerializerMethodField()

    def get_gov_id_front(self, obj):
        request = self.context.get('request')
        if obj.gov_id_front and hasattr(obj.gov_id_front, 'url'):
            return request.build_absolute_uri(obj.gov_id_front.url) if request else obj.gov_id_front.url
        return None

    def get_gov_id_back(self, obj):
        request = self.context.get('request')
        if obj.gov_id_back and hasattr(obj.gov_id_back, 'url'):
            return request.build_absolute_uri(obj.gov_id_back.url) if request else obj.gov_id_back.url
        return None

    class Meta:
        model = Member
        fields = [
            "id",
            "member_id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "phone",
            "address",
            "join_date",
            "is_active_member",
            "remaining_days",
            "remaining_days_updated_at",
            "gov_id_front",
            "gov_id_back",
        ]
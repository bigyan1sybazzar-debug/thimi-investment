from django.contrib import admin
from .models import Member, GlobalSetting, RelatedDocument


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'get_full_name', 'get_username', 'get_email', 'phone', 'is_active_member')

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return name if name else obj.user.username

    @admin.display(description='Username')
    def get_username(self, obj):
        return obj.user.username

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email


admin.site.register(GlobalSetting)


@admin.register(RelatedDocument)
class RelatedDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'uploaded_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
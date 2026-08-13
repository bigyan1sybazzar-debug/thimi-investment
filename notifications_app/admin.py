from django.contrib import admin
from .models import SystemNotification

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'user', 'created_at', 'is_read')
    list_filter = ('category', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')


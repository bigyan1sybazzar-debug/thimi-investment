from django.urls import path
from .views import (
    NotificationStatusView,
    SendPaymentRemindersView,
    SendBroadcastEmailView,
    ServerIPView,
    SMTPDiagnosticView,
    SystemNotificationListView,
    SendMemberMessageView,
    AdminReplyMessageView,
)

urlpatterns = [
    path('status/', NotificationStatusView.as_view(), name='notification_status'),
    path('send-reminders/', SendPaymentRemindersView.as_view(), name='send_reminders'),
    path('send-broadcast/', SendBroadcastEmailView.as_view(), name='send_broadcast'),
    path('messages/', SystemNotificationListView.as_view(), name='system_messages'),
    path('send-message/', SendMemberMessageView.as_view(), name='send_member_message'),
    path('reply/<int:pk>/', AdminReplyMessageView.as_view(), name='admin_reply_message'),
    path('server-ip/', ServerIPView.as_view(), name='server_ip'),
    path('smtp-diagnostic/', SMTPDiagnosticView.as_view(), name='smtp_diagnostic'),
]





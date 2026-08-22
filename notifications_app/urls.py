from django.urls import path
from .views import (
    NotificationStatusView,
    SendPaymentRemindersView,
    SendBroadcastEmailView,
    ServerIPView,
    SystemNotificationListView,
    SendMemberMessageView,
    AdminReplyMessageView,
    SendMeetingAnnouncementView,
    GenerateTeamsMeetingView,
)

urlpatterns = [
    path('status/', NotificationStatusView.as_view(), name='notification_status'),
    path('send-reminders/', SendPaymentRemindersView.as_view(), name='send_reminders'),
    path('send-broadcast/', SendBroadcastEmailView.as_view(), name='send_broadcast'),
    path('send-meeting/', SendMeetingAnnouncementView.as_view(), name='send_meeting'),
    path('generate-teams-meeting/', GenerateTeamsMeetingView.as_view(), name='generate_teams_meeting'),
    path('messages/', SystemNotificationListView.as_view(), name='system_messages'),
    path('send-message/', SendMemberMessageView.as_view(), name='send_member_message'),
    path('reply/<int:pk>/', AdminReplyMessageView.as_view(), name='admin_reply_message'),
    path('server-ip/', ServerIPView.as_view(), name='server_ip'),
]





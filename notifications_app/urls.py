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
    CreateMeetingPollView,
    MeetingPollListView,
    CastPollVoteView,
    MeetingPollDetailView,
    ChatMessagesView,
    SuggestMeetingPollOptionView,
    FinalizeMeetingPollView,
    BroadcastPollInviteView,
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
    # Meeting Polls
    path('polls/', MeetingPollListView.as_view(), name='poll_list'),
    path('polls/create/', CreateMeetingPollView.as_view(), name='poll_create'),
    path('polls/vote/', CastPollVoteView.as_view(), name='poll_vote'),
    path('polls/suggest/', SuggestMeetingPollOptionView.as_view(), name='poll_suggest'),
    path('polls/finalize/', FinalizeMeetingPollView.as_view(), name='poll_finalize'),
    path('polls/<int:pk>/broadcast/', BroadcastPollInviteView.as_view(), name='poll_broadcast'),
    path('polls/<int:pk>/', MeetingPollDetailView.as_view(), name='poll_detail'),
    # Member Chat
    path('chat/', ChatMessagesView.as_view(), name='chat_messages'),
]






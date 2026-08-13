from django.urls import path
from .views import (
    NotificationStatusView,
    SendPaymentRemindersView,
    SendBroadcastEmailView,
)

urlpatterns = [
    path('status/', NotificationStatusView.as_view(), name='notification_status'),
    path('send-reminders/', SendPaymentRemindersView.as_view(), name='send_reminders'),
    path('send-broadcast/', SendBroadcastEmailView.as_view(), name='send_broadcast'),
]

from django.db import models
from django.contrib.auth.models import User
from accounts.models import Member

class SystemNotification(models.Model):
    CATEGORY_CHOICES = (
        ('profile_update', 'Profile Update'),
        ('deposit', 'Deposit'),
        ('loan', 'Loan'),
        ('system', 'System'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='profile_update')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category}] {self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class MeetingPoll(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    venue = models.CharField(max_length=255, default='Online via Zoom/Teams')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    final_option = models.ForeignKey('MeetingPollOption', on_delete=models.SET_NULL, null=True, blank=True, related_name='finalized_for_poll')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Poll: {self.title} (Active: {self.is_active})"


class MeetingPollOption(models.Model):
    poll = models.ForeignKey(MeetingPoll, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)  # e.g., "Saturday 10:00 AM"
    suggested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='suggested_options')

    def __str__(self):
        return f"{self.poll.title} - {self.option_text}"


class MeetingPollVote(models.Model):
    poll = models.ForeignKey(MeetingPoll, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.ForeignKey(MeetingPollOption, on_delete=models.CASCADE, related_name='votes')
    voted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('poll', 'user')

    def __str__(self):
        return f"{self.user.username} voted for {self.option.option_text}"


class MemberChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}"


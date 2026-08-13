from django.db import models
from django.contrib.auth.models import User

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


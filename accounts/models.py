from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Member(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )

    member_id = models.CharField(
        max_length=20,
        unique=True
    )

    phone = models.CharField(max_length=20)

    address = models.TextField()

    join_date = models.DateField(auto_now_add=True)

    is_active_member = models.BooleanField(default=True)

    remaining_days = models.IntegerField(default=0)

    remaining_days_updated_at = models.DateField(null=True, blank=True)

    gov_id_front = models.ImageField(upload_to='gov_ids/', null=True, blank=True)
    gov_id_back = models.ImageField(upload_to='gov_ids/', null=True, blank=True)

    def __str__(self):
        return f"{self.member_id} - {self.user.username}"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                orig = Member.objects.get(pk=self.pk)
                if orig.remaining_days != self.remaining_days:
                    self.remaining_days_updated_at = timezone.now().date()
            except Member.DoesNotExist:
                self.remaining_days_updated_at = timezone.now().date()
        else:
            self.remaining_days_updated_at = timezone.now().date()
        super().save(*args, **kwargs)


class GlobalSetting(models.Model):
    remaining_days = models.IntegerField(default=0)
    remaining_days_updated_at = models.DateField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr/', null=True, blank=True)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"Global Settings (Remaining Days: {self.remaining_days})"


    def save(self, *args, **kwargs):
        if self.pk:
            try:
                orig = GlobalSetting.objects.get(pk=self.pk)
                if orig.remaining_days != self.remaining_days:
                    self.remaining_days_updated_at = timezone.now().date()
            except GlobalSetting.DoesNotExist:
                self.remaining_days_updated_at = timezone.now().date()
        else:
            self.remaining_days_updated_at = timezone.now().date()
        super().save(*args, **kwargs)


class RelatedDocument(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
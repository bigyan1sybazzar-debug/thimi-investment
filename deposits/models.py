from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Member


class Deposit(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    PAYMENT_METHODS = [
        ("cash", "Cash"),
        ("esewa", "eSewa"),
        ("khalti", "Khalti"),
        ("bank", "Bank Transfer"),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="deposits"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    saving_year = models.PositiveIntegerField(
        default=timezone.now().year
    )

    saving_month = models.PositiveSmallIntegerField(
        default=timezone.now().month
    )

    payment_date = models.DateField(
        default=timezone.now
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="cash"
    )

    screenshot = models.ImageField(
        upload_to="deposits/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_deposits"
    )

    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["member", "saving_year", "saving_month"],
                name="unique_member_month_deposit"
            )
        ]

    def __str__(self):
        return f"{self.member.member_id} - {self.saving_month}/{self.saving_year}"


class Expense(models.Model):
    """Group expenses tracked by admin, visible to all members."""

    CATEGORY_CHOICES = [
        ("operational", "Operational"),
        ("meeting", "Meeting / Event"),
        ("stationery", "Stationery / Supplies"),
        ("travel", "Travel / Transport"),
        ("fee", "Bank / Service Fee"),
        ("fine", "Penalty / Fine"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default="other"
    )
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    receipt = models.ImageField(
        upload_to="expenses/", blank=True, null=True
    )
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="added_expenses"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} — Rs.{self.amount} ({self.date})"
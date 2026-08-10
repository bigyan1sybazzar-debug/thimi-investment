from django.db import models


class Loan(models.Model):
    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Closed", "Closed"),
        ("Pending", "Pending"),
    ]

    name = models.CharField(max_length=150, help_text="Borrower's full name")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    disbursement_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    interest_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    annual_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.12,
        help_text="e.g. 0.12 for 12%"
    )
    tenure_years = models.DecimalField(max_digits=4, decimal_places=2, default=0.5)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-disbursement_date"]

    def __str__(self):
        return f"{self.name} — Rs.{self.amount} ({self.status})"

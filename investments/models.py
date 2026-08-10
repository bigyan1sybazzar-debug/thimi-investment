from django.db import models


class StockTransaction(models.Model):
    STATUS_CHOICES = [
        ("Holding", "Holding"),
        ("Sold", "Sold"),
        ("Loss", "Loss"),
    ]

    date = models.DateField(help_text="Transaction date (can be Nepali calendar string)")
    symbol = models.CharField(max_length=20, help_text="Stock symbol e.g. PRVU")
    shares = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    buy_amount_with_tax = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sell_amount_after_tax = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    profit_loss = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Holding")
    remarks = models.CharField(max_length=150, blank=True, null=True, help_text="e.g. Pradeep / Pawan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "symbol"]

    def __str__(self):
        return f"{self.date} — {self.symbol} x{self.shares} ({self.status})"


class ShareInventory(models.Model):
    stock = models.CharField(max_length=20, unique=True, help_text="Stock symbol")
    no_of_kitta = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["stock"]

    def __str__(self):
        return f"{self.stock}: {self.no_of_kitta} kitta"

from django.db import models


class Member(models.Model):
    STATUS_CHOICES = (
        ("Active", "Active"),
        ("Inactive", "Inactive"),
    )

    member_id = models.CharField(max_length=10, unique=True)
    full_name = models.CharField(max_length=150)
    father_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)

    address = models.TextField(blank=True)

    citizenship_no = models.CharField(max_length=50, blank=True)

    joined_date = models.DateField()

    photo = models.ImageField(
        upload_to="members/",
        blank=True,
        null=True
    )

    nominee_name = models.CharField(max_length=150, blank=True)
    nominee_phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["member_id"]

    def __str__(self):
        return f"{self.member_id} - {self.full_name}"

import uuid

from django.conf import settings
from django.db import models

from apps.catalog.models import Course


class Order(models.Model):
    """One purchase attempt for one course. A course is unlocked for a
    student once an Order for it reaches status=SUCCESS."""

    class Gateway(models.TextChoices):
        ESEWA = "esewa", "eSewa"
        KHALTI = "khalti", "Khalti"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="orders")
    transaction_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    gateway = models.CharField(max_length=10, choices=Gateway.choices)
    gateway_reference = models.CharField(
        max_length=200, blank=True, help_text="Gateway's own transaction/token id (e.g. Khalti pidx)."
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.course} ({self.status})"

    def mark_success(self, gateway_reference=""):
        self.status = self.Status.SUCCESS
        if gateway_reference:
            self.gateway_reference = gateway_reference
        self.save(update_fields=["status", "gateway_reference", "updated_at"])

    def mark_failed(self, gateway_reference=""):
        self.status = self.Status.FAILED
        if gateway_reference:
            self.gateway_reference = gateway_reference
        self.save(update_fields=["status", "gateway_reference", "updated_at"])

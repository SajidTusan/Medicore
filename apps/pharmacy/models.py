from django.db import models
from django.conf import settings
from apps.medical_records.models import Prescription

class Medicine(models.Model):

    name = models.CharField(
        max_length=200,
    )

    generic_name = models.CharField(
        max_length=200,
        blank=True,
    )

    strength = models.CharField(
        max_length=100,
        blank=True,
    )

    unit = models.CharField(
        max_length=50,
        default="unit",
    )

    stock_quantity = models.PositiveIntegerField(
        default=0,
    )

    reorder_level = models.PositiveIntegerField(
        default=10,
    )

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name} {self.strength}".strip()

class DispensingRecord(models.Model):

    class Status(models.TextChoices):
        DISPENSED = "DISPENSED", "Dispensed"
        PARTIAL = "PARTIAL", "Partially Dispensed"
        CANCELLED = "CANCELLED", "Cancelled"

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.PROTECT,
        related_name="dispensing_records",
    )

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name="dispensing_records",
    )

    pharmacist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="dispensed_medicines",
    )

    quantity = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DISPENSED,
    )

    notes = models.TextField(
        blank=True,
    )

    dispensed_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.prescription.prescription_id} - "
            f"{self.medicine.name} - "
            f"{self.quantity}"
        )
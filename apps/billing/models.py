from django.conf import settings
from django.db import models

from apps.appointments.models import Appointment
from apps.medical_records.models import Consultation


class Bill(models.Model):

    class Status(models.TextChoices):
        UNPAID = "UNPAID", "Unpaid"
        PARTIAL = "PARTIAL", "Partially Paid"
        PAID = "PAID", "Paid"
        CANCELLED = "CANCELLED", "Cancelled"

    bill_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="bills",
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bills",
    )

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bills",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    lab_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    medicine_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    other_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPAID,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        return (
            self.consultation_fee
            + self.lab_fee
            + self.medicine_fee
            + self.other_fee
        )

    def update_status(self):
        if self.paid_amount <= 0:
            self.status = self.Status.UNPAID
        elif self.paid_amount < self.total_amount:
            self.status = self.Status.PARTIAL
        else:
            self.status = self.Status.PAID

    def save(self, *args, **kwargs):

        if not self.bill_id:
            last_bill = Bill.objects.order_by("-id").first()
            number = last_bill.id + 1 if last_bill else 1
            self.bill_id = f"BILL-{number:06d}"

        self.total_amount = self.calculate_total()
        self.update_status()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bill_id} - {self.patient.public_id}"


class Payment(models.Model):

    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        MOBILE_BANKING = "MOBILE_BANKING", "Mobile Banking"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"

    bill = models.ForeignKey(
        Bill,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    method = models.CharField(
        max_length=30,
        choices=Method.choices,
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(blank=True)

    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_payments",
    )

    paid_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.bill.bill_id} - {self.amount}"
from django.conf import settings
from django.db import models

from apps.appointments.models import Appointment


class Consultation(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.PROTECT,
        related_name="consultation",
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="consultations",
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="doctor_consultations",
    )

    chief_complaint = models.TextField(
        help_text="Main reason or complaint of the patient."
    )

    symptoms = models.TextField(
        blank=True,
    )

    diagnosis = models.TextField(
        blank=True,
    )

    clinical_notes = models.TextField(
        blank=True,
    )

    follow_up_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Consultation - "
            f"{self.patient.public_id} - "
            f"{self.appointment.date}"
        )

class PharmacyStatus(models.TextChoices):
    NOT_DISPENSED = "NOT_DISPENSED", "Not Dispensed"
    PARTIALLY_DISPENSED = "PARTIALLY_DISPENSED", "Partially Dispensed"
    DISPENSED = "DISPENSED", "Dispensed"

class Prescription(models.Model):

    class PharmacyStatus(models.TextChoices):
        NOT_DISPENSED = "NOT_DISPENSED", "Not Dispensed"
        PARTIALLY_DISPENSED = "PARTIALLY_DISPENSED", "Partially Dispensed"

        DISPENSED = "DISPENSED", "Dispensed"

    consultation = models.OneToOneField(
        Consultation,
        on_delete=models.PROTECT,
        related_name="prescription",
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="prescriptions",
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="doctor_prescriptions",
    )

    prescription_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
    )

    pharmacy_status = models.CharField(
        max_length=30,
        choices=PharmacyStatus.choices,
        default=PharmacyStatus.NOT_DISPENSED,
    )

    advice = models.TextField(blank=True)
    tests_advised = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if not self.prescription_id:

            last_prescription = (
                Prescription.objects
                .order_by("-id")
                .first()
            )

            if last_prescription:
                number = last_prescription.id + 1
            else:
                number = 1

            self.prescription_id = f"RX-{number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.prescription_id


class PrescriptionMedicine(models.Model):

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="medicines",
    )

    medicine_name = models.CharField(
        max_length=200,
    )

    dosage = models.CharField(
        max_length=100,
    )

    frequency = models.CharField(
        max_length=100,
    )

    duration = models.CharField(
        max_length=100,
    )

    instructions = models.TextField(
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.medicine_name} - "
            f"{self.dosage}"
        )
class LabTest(models.Model):

    name = models.CharField(
        max_length=200,
    )

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.name} ({self.code})"

class LabTestOrder(models.Model):

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        SAMPLE_COLLECTED = "SAMPLE_COLLECTED", "Sample Collected"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lab_test_orders",
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ordered_lab_tests",
    )

    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.PROTECT,
        related_name="lab_test_orders",
        null=True,
        blank=True,
    )

    test = models.ForeignKey(
        LabTest,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    order_id = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.REQUESTED,
    )

    result = models.TextField(
        blank=True,
    )

    result_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def save(self, *args, **kwargs):

        if not self.order_id:

            last_order = (
                LabTestOrder.objects
                .order_by("-id")
                .first()
            )

            if last_order:
                number = last_order.id + 1
            else:
                number = 1

            self.order_id = f"LAB-{number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id
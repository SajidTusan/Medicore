from django.conf import settings
from django.db import models

from apps.doctors.models import DoctorProfile
from apps.hospitals.models import Department


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
    )

    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    reason = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.patient.public_id} - "
            f"Dr. {self.doctor.user.get_full_name()} - "
            f"{self.date} {self.start_time}"
        )

    class Meta:
        ordering = ["date", "start_time"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "doctor",
                    "date",
                    "start_time",
                    "end_time",
                ],
                condition=models.Q(
                    status__in=[
                        "PENDING",
                        "CONFIRMED",
                    ]
                ),
                name="unique_active_doctor_appointment_slot",
            ),
        ]
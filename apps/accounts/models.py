from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    DOCTOR = "DOCTOR", "Doctor"
    NURSE = "NURSE", "Nurse"
    PATIENT = "PATIENT", "Patient"
    LAB = "LAB", "Laboratory Staff"
    PHARMACIST = "PHARMACIST", "Pharmacist"
    RECEPTIONIST = "RECEPTIONIST", "Receptionist"

class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
    )

    public_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"
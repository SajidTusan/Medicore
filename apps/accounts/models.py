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

    def save(self, *args, **kwargs):

        if not self.public_id:

            prefixes = {
                self.Role.ADMIN: "ADM",
                self.Role.DOCTOR: "DOC",
                self.Role.NURSE: "NUR",
                self.Role.PATIENT: "PAT",
                self.Role.LAB: "LAB",
                self.Role.PHARMACIST: "PHA",
                self.Role.RECEPTIONIST: "REC",
            }

            prefix = prefixes.get(
                self.role,
                "USR",
            )

            last_user = (
                User.objects
                .filter(public_id__startswith=prefix)
                .order_by("-id")
                .first()
            )

            if last_user and last_user.public_id:
                try:
                    number = int(
                        last_user.public_id[-6:]
                    ) + 1
                except ValueError:
                    number = 1
            else:
                number = 1

            self.public_id = (
                f"{prefix}-{number:06d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
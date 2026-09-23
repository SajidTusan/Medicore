from django.conf import settings
from django.db import models

class DoctorProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
    )

    specialization = models.CharField(
        max_length=100,
        blank=True,
    )

    qualification = models.CharField(
        max_length=255,
        blank=True,
    )

    experience_years = models.PositiveIntegerField(
        default=0,
    )

    license_number = models.CharField(
        max_length=100,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.user.public_id}"
from django.conf import settings
from django.db import models

class NurseProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nurse_profile",
    )

    qualification = models.CharField(
        max_length=255,
        blank=True,
    )

    experience_years = models.PositiveIntegerField(
        default=0,
    )

    skills = models.TextField(
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    is_available_for_homecare = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.public_id}"
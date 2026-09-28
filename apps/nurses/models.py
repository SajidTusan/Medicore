from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.hospitals.models import Hospital


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
        help_text="Example: Elderly Care, Patient Care, Injection, Wound Care",
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nurse_profiles",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )

    total_reviews = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    updated_at = models.DateTimeField(
        default=timezone.now,
    )

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.public_id}"

class HomeCareAvailability(models.Model):

    class Day(models.TextChoices):
        SATURDAY = "SATURDAY", "Saturday"
        SUNDAY = "SUNDAY", "Sunday"
        MONDAY = "MONDAY", "Monday"
        TUESDAY = "TUESDAY", "Tuesday"
        WEDNESDAY = "WEDNESDAY", "Wednesday"
        THURSDAY = "THURSDAY", "Thursday"
        FRIDAY = "FRIDAY", "Friday"

    nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.CASCADE,
        related_name="home_care_availability",
    )

    day = models.CharField(
        max_length=10,
        choices=Day.choices,
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    is_active = models.BooleanField(
        default=True,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "day",
            "start_time",
        ]

    def __str__(self):
        return (
            f"{self.nurse.user.public_id} - "
            f"{self.day} - "
            f"{self.start_time} to {self.end_time}"
        )

class HomeCareRequest(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        REJECTED = "REJECTED", "Rejected"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="home_care_requests",
    )

    nurse = models.ForeignKey(
        NurseProfile,
        on_delete=models.PROTECT,
        related_name="home_care_requests",
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    location = models.TextField()

    required_skills = models.TextField(
        blank=True,
    )

    patient_notes = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        default=timezone.now,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.patient.public_id} → "
            f"{self.nurse.user.public_id} - "
            f"{self.date}"
        )
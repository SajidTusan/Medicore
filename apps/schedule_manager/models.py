from django.conf import settings
from django.db import models

from apps.hospitals.models import Hospital, Department


class Schedule(models.Model):

    class ScheduleType(models.TextChoices):
        HOSPITAL_DUTY = "HOSPITAL_DUTY", "Hospital Duty"
        HOME_CARE = "HOME_CARE", "Home Care"
        LEAVE = "LEAVE", "Leave"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schedules",
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedules",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedules",
    )

    date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    schedule_type = models.CharField(
        max_length=20,
        choices=ScheduleType.choices,
    )

    is_active = models.BooleanField(
        default=True,
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

    class Meta:
        ordering = [
            "date",
            "start_time",
        ]

    def __str__(self):
        return (
            f"{self.user.public_id} - "
            f"{self.date} - "
            f"{self.start_time} to {self.end_time}"
        )
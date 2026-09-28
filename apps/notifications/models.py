from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        HOME_CARE = "HOME_CARE", "Home Care"
        APPOINTMENT = "APPOINTMENT", "Appointment"
        REVIEW = "REVIEW", "Review"
        LAB = "LAB", "Laboratory"
        PHARMACY = "PHARMACY", "Pharmacy"
        BILLING = "BILLING", "Billing"
        SYSTEM = "SYSTEM", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    link = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional URL/path related to this notification.",
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.public_id} - {self.title}"
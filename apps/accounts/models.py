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
        # যদি ইউজারটি সুপারইউজার হয়, তবে তার রোল স্বয়ংক্রিয়ভাবে ADMIN করে দেওয়া হচ্ছে
        if self.is_superuser and self.role == Role.PATIENT:
            self.role = Role.ADMIN
            self.is_verified = True  # সুপারইউজারকে অটো-ভেরিফাইড মার্ক করা হলো

        if not self.public_id:
            # এখানে self.Role এর পরিবর্তে সরাসরি Role ক্লাস ব্যবহার করা হয়েছে
            prefixes = {
                Role.ADMIN: "ADM",
                Role.DOCTOR: "DOC",
                Role.NURSE: "NUR",
                Role.PATIENT: "PAT",
                Role.LAB: "LAB",
                Role.PHARMACIST: "PHA",
                Role.RECEPTIONIST: "REC",
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

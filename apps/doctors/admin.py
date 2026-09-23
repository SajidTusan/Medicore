from django.contrib import admin

from .models import DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "hospital",
        "department",
        "specialization",
        "experience_years",
        "consultation_fee",
    )
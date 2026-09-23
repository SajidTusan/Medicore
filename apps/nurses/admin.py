from django.contrib import admin
from .models import NurseProfile


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "qualification",
        "experience_years",
        "is_available_for_homecare",
    )
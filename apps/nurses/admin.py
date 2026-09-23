from django.contrib import admin

from .models import NurseProfile


@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "hospital",
        "department",
        "qualification",
        "experience_years",
        "is_available_for_homecare",
    )

    list_filter = (
        "hospital",
        "department",
        "is_available_for_homecare",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__public_id",
        "phone",
    )
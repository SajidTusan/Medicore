from django.contrib import admin

from .models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "hospital",
        "department",
        "date",
        "start_time",
        "end_time",
        "schedule_type",
        "is_active",
    )

    list_filter = (
        "schedule_type",
        "hospital",
        "department",
        "date",
        "is_active",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__public_id",
    )

    ordering = (
        "date",
        "start_time",
    )
from django.contrib import admin
from .models import Hospital, Department


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "phone",
        "is_active",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "hospital",
        "code",
        "is_active",
    )
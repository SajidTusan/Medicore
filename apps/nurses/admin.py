from django.contrib import admin
from .models import NurseProfile

@admin.register(NurseProfile)
class NurseProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "hospital",
        "get_department",          
        "qualification",
        "experience_years",
        "check_homecare_status",     
    )

    list_filter = (
        "hospital",
        "qualification",
        "experience_years",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__public_id",
        "phone",
    )

    @admin.display(description="Department")
    def get_department(self, obj):
        if obj.hospital and hasattr(obj.hospital, 'department'):
            return obj.hospital.department
        return "N/A"

    @admin.display(description="Homecare Available", boolean=True)
    def check_homecare_status(self, obj):
        return obj.home_care_availability.filter(is_active=True).exists()

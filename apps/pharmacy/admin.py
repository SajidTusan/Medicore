from django.contrib import admin
from .models import Medicine
from .models import Medicine, DispensingRecord

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "generic_name",
        "strength",
        "stock_quantity",
        "reorder_level",
        "expiry_date",
        "is_active",
    )

    search_fields = (
        "name",
        "generic_name",
        "strength",
    )

    list_filter = (
        "is_active",
        "expiry_date",
    )

@admin.register(DispensingRecord)
class DispensingRecordAdmin(admin.ModelAdmin):

    list_display = (
        "prescription",
        "medicine",
        "pharmacist",
        "quantity",
        "status",
        "dispensed_at",
    )

    search_fields = (
        "prescription__prescription_id",
        "medicine__name",
        "pharmacist__username",
    )

    list_filter = (
        "status",
        "dispensed_at",
    )
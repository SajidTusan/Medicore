from django.contrib import admin
from .models import LabTest, LabTestOrder
from .models import (Consultation,Prescription,PrescriptionMedicine,)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "appointment",
        "patient",
        "doctor",
        "follow_up_date",
        "created_at",
    )

    search_fields = (
        "patient__username",
        "patient__public_id",
        "doctor__username",
        "doctor__public_id",
    )

    list_filter = (
        "follow_up_date",
        "created_at",
    )
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):

    list_display = (
        "prescription_id",
        "patient",
        "doctor",
        "follow_up_date",
        "created_at",
    )

    search_fields = (
        "prescription_id",
        "patient__username",
        "patient__public_id",
        "doctor__username",
        "doctor__public_id",
    )

    list_filter = (
        "follow_up_date",
        "created_at",
    )


@admin.register(PrescriptionMedicine)
class PrescriptionMedicineAdmin(admin.ModelAdmin):

    list_display = (
        "prescription",
        "medicine_name",
        "dosage",
        "frequency",
        "duration",
    )

    search_fields = (
        "medicine_name",
        "prescription__prescription_id",
    )

@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
    )

    list_filter = (
        "is_active",
    )
@admin.register(LabTestOrder)
class LabTestOrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_id",
        "patient",
        "doctor",
        "test",
        "status",
        "created_at",
    )

    search_fields = (
        "order_id",
        "patient__username",
        "patient__public_id",
        "doctor__username",
    )

    list_filter = (
        "status",
        "test",
    )

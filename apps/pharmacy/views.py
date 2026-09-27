from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.medical_records.models import Prescription
from .forms import DispenseMedicineForm
from .models import DispensingRecord, Medicine


@login_required
def pharmacy_prescriptions(request):
    if request.user.role != "PHARMACIST":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    prescriptions = (
        Prescription.objects
        .select_related(
            "patient",
            "doctor",
            "consultation",
        )
        .prefetch_related(
            "medicines",
        )
        .order_by(
            "-created_at",
        )
    )

    return render(
        request,
        "pharmacy/prescriptions.html",
        {
            "prescriptions": prescriptions,
        },
    )


@login_required
def dispense_prescription(request, prescription_id):
    if request.user.role != "PHARMACIST":
        return render(request, "errors/403.html", status=403)

    prescription = get_object_or_404(
        Prescription.objects
        .select_related("patient", "doctor")
        .prefetch_related("medicines"),
        id=prescription_id,
    )

    if request.method == "POST":
        form = DispenseMedicineForm(
            request.POST,
            prescription=prescription,
        )

        if form.is_valid():
            medicine = form.cleaned_data["medicine"]
            quantity = form.cleaned_data["quantity"]

            with transaction.atomic():

                medicine = (
                    medicine.__class__.objects
                    .select_for_update()
                    .get(pk=medicine.pk)
                )

                if (
                    medicine.expiry_date
                    and medicine.expiry_date < timezone.localdate()
                ):
                    form.add_error(
                        "medicine",
                        "This medicine has expired and cannot be dispensed.",
                    )

                elif quantity > medicine.stock_quantity:
                    form.add_error(
                        "quantity",
                        f"Only {medicine.stock_quantity} "
                        f"{medicine.unit}(s) are available.",
                    )

                else:
                    medicine.stock_quantity -= quantity

                    medicine.save(
                        update_fields=[
                            "stock_quantity",
                            "updated_at",
                        ]
                    )

                    DispensingRecord.objects.create(
                        prescription=prescription,
                        medicine=medicine,
                        pharmacist=request.user,
                        quantity=quantity,
                        notes=form.cleaned_data["notes"],
                    )

                    # স্ট্যাটাস আপডেট লজিক এখানে যুক্ত করা হলো
                    prescribed_names = {
                        name.strip().lower()
                        for name in prescription.medicines.values_list(
                            "medicine_name",
                            flat=True,
                        )
                    }
                    dispensed_names = {
                        name.strip().lower()
                        for name in DispensingRecord.objects.filter(
                            prescription=prescription,
                            status=DispensingRecord.Status.DISPENSED,
                        ).values_list(
                            "medicine__name",
                            flat=True,
                        )
                    }

                    if prescribed_names and prescribed_names.issubset(dispensed_names):
                        prescription.pharmacy_status = Prescription.PharmacyStatus.DISPENSED
                    else:
                        prescription.pharmacy_status = (
                            Prescription.PharmacyStatus.PARTIALLY_DISPENSED
                        )

                    prescription.save(update_fields=["pharmacy_status", "updated_at"])

                    messages.success(
                        request,
                        f"{quantity} {medicine.name} dispensed successfully.",
                    )

                    if medicine.stock_quantity <= medicine.reorder_level:
                        messages.warning(
                            request,
                            f"{medicine.name} is now low in stock. "
                            f"Remaining: {medicine.stock_quantity} {medicine.unit}(s).",
                        )

                    return redirect("pharmacy:prescriptions")

    else:
        form = DispenseMedicineForm(
            prescription=prescription,
        )

    return render(
        request,
        "pharmacy/dispense.html",
        {
            "prescription": prescription,
            "form": form,
        },
    )
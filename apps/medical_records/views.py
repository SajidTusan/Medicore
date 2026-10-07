from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.appointments.models import Appointment
from apps.medical_records.permissions import doctor_has_patient_relationship

from .forms import (
    ConsultationForm,
    LabOrderUpdateForm,
    PrescriptionForm,
    PrescriptionMedicineFormSet,
    LabTestOrderForm,
)
from .models import (
    Consultation,
    Prescription,
    PrescriptionMedicine,
    LabTestOrder,
)


@login_required
def create_consultation(request, appointment_id):
    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            "patient",
            "doctor__user",
            "department",
        ),
        id=appointment_id,
        doctor__user=request.user,
    )

    if appointment.status != Appointment.Status.CONFIRMED:
        return render(
            request,
            "errors/400.html",
            status=400,
        )

    existing_consultation = Consultation.objects.filter(
        appointment=appointment
    ).first()

    if existing_consultation:
        return redirect(
            "medical_records:consultation_detail",
            consultation_id=existing_consultation.id,
        )

    if request.method == "POST":
        form = ConsultationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                locked_appointment = get_object_or_404(
                    Appointment.objects.select_for_update(),
                    id=appointment.id,
                    doctor__user=request.user,
                )

                if locked_appointment.status != Appointment.Status.CONFIRMED:
                    return render(
                        request,
                        "errors/400.html",
                        status=400,
                    )

                existing_consultation = (
                    Consultation.objects
                    .filter(appointment=locked_appointment)
                    .first()
                )

                if existing_consultation:
                    return redirect(
                        "medical_records:consultation_detail",
                        consultation_id=existing_consultation.id,
                    )

                consultation = form.save(commit=False)
                consultation.appointment = locked_appointment
                consultation.patient = locked_appointment.patient
                consultation.doctor = request.user
                consultation.save()

            return redirect(
                "medical_records:consultation_detail",
                consultation_id=consultation.id,
            )

    else:
        form = ConsultationForm()

    previous_consultations = (
        Consultation.objects
        .filter(patient=appointment.patient)
        .exclude(appointment=appointment)
        .select_related(
            "doctor",
            "appointment",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "medical_records/consultation_form.html",
        {
            "form": form,
            "appointment": appointment,
            "previous_consultations": previous_consultations,
        },
    )


@login_required
def consultation_detail(request, consultation_id):
    consultation = get_object_or_404(
        Consultation.objects.select_related(
            "patient",
            "doctor",
            "appointment",
        ),
        id=consultation_id,
    )

    if (
        request.user != consultation.doctor
        and request.user != consultation.patient
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    return render(
        request,
        "medical_records/consultation_detail.html",
        {
            "consultation": consultation,
        },
    )


@login_required
def create_prescription(request, consultation_id):
    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    consultation = get_object_or_404(
        Consultation.objects.select_related(
            "patient",
            "doctor",
            "appointment",
        ),
        id=consultation_id,
        doctor=request.user,
    )

    existing_prescription = Prescription.objects.filter(
        consultation=consultation,
    ).first()

    if existing_prescription:
        return redirect(
            "medical_records:prescription_detail",
            prescription_id=existing_prescription.id,
        )

    if request.method == "POST":
        prescription_form = PrescriptionForm(request.POST)
        medicine_formset = PrescriptionMedicineFormSet(request.POST)

        if (
            prescription_form.is_valid()
            and medicine_formset.is_valid()
        ):
            valid_medicines = [
                form.cleaned_data
                for form in medicine_formset
                if form.cleaned_data
                and not form.cleaned_data.get("DELETE")
            ]

            if not valid_medicines:
                medicine_formset.non_form_errors = lambda: [
                    "At least one medicine is required."
                ]

            else:
                with transaction.atomic():
                    locked_consultation = get_object_or_404(
                        Consultation.objects
                        .select_for_update()
                        .select_related(
                            "patient",
                            "doctor",
                            "appointment",
                        ),
                        id=consultation.id,
                        doctor=request.user,
                    )

                    if (
                        locked_consultation.appointment.status
                        != Appointment.Status.CONFIRMED
                    ):
                        return render(
                            request,
                            "errors/400.html",
                            status=400,
                        )

                    existing_prescription = (
                        Prescription.objects
                        .filter(
                            consultation=locked_consultation
                        )
                        .first()
                    )

                    if existing_prescription:
                        return redirect(
                            "medical_records:prescription_detail",
                            prescription_id=existing_prescription.id,
                        )

                    prescription = Prescription.objects.create(
                        consultation=locked_consultation,
                        patient=locked_consultation.patient,
                        doctor=request.user,
                        advice=prescription_form.cleaned_data[
                            "advice"
                        ],
                        tests_advised=prescription_form.cleaned_data[
                            "tests_advised"
                        ],
                        follow_up_date=prescription_form.cleaned_data[
                            "follow_up_date"
                        ],
                    )

                    for medicine in valid_medicines:
                        PrescriptionMedicine.objects.create(
                            prescription=prescription,
                            medicine_name=medicine["medicine_name"],
                            dosage=medicine["dosage"],
                            frequency=medicine["frequency"],
                            duration=medicine["duration"],
                            instructions=medicine["instructions"],
                        )

                return redirect(
                    "medical_records:prescription_detail",
                    prescription_id=prescription.id,
                )

    else:
        prescription_form = PrescriptionForm()
        medicine_formset = PrescriptionMedicineFormSet()

    return render(
        request,
        "medical_records/prescription_form.html",
        {
            "consultation": consultation,
            "prescription_form": prescription_form,
            "medicine_formset": medicine_formset,
        },
    )


@login_required
def prescription_detail(request, prescription_id):
    prescription = get_object_or_404(
        Prescription.objects.select_related(
            "patient",
            "doctor",
            "consultation",
        ).prefetch_related("medicines"),
        id=prescription_id,
    )

    if request.user.role == "PATIENT":
        if prescription.patient != request.user:
            return render(
                request,
                "errors/403.html",
                status=403,
            )

    elif request.user.role == "DOCTOR":
        if prescription.doctor != request.user:
            return render(
                request,
                "errors/403.html",
                status=403,
            )

    else:
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    return render(
        request,
        "medical_records/prescription_detail.html",
        {
            "prescription": prescription,
        },
    )


@login_required
def create_lab_order(request, consultation_id):
    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    consultation = get_object_or_404(
        Consultation.objects.select_related(
            "patient",
            "doctor",
            "appointment",
        ),
        id=consultation_id,
        doctor=request.user,
    )

    if request.method == "POST":
        form = LabTestOrderForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                locked_consultation = get_object_or_404(
                    Consultation.objects
                    .select_for_update()
                    .select_related(
                        "patient",
                        "doctor",
                        "appointment",
                    ),
                    id=consultation.id,
                    doctor=request.user,
                )

                if (
                    locked_consultation.appointment.status
                    != Appointment.Status.CONFIRMED
                ):
                    return render(
                        request,
                        "errors/400.html",
                        status=400,
                    )

                LabTestOrder.objects.create(
                    patient=locked_consultation.patient,
                    doctor=request.user,
                    consultation=locked_consultation,
                    test=form.cleaned_data["test"],
                    notes=form.cleaned_data["notes"],
                )

            return redirect(
                "medical_records:consultation_detail",
                consultation_id=locked_consultation.id,
            )

    else:
        form = LabTestOrderForm()

    return render(
        request,
        "medical_records/lab_order_form.html",
        {
            "form": form,
            "consultation": consultation,
        },
    )


@login_required
def lab_orders(request):
    if request.user.role != "LAB":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    orders = (
        LabTestOrder.objects
        .select_related(
            "patient",
            "doctor",
            "test",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "medical_records/lab_orders.html",
        {
            "orders": orders,
        },
    )


@login_required
def update_lab_order(request, order_id):
    if request.user.role != "LAB":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    order = get_object_or_404(
        LabTestOrder.objects.select_related(
            "patient",
            "doctor",
            "test",
        ),
        id=order_id,
    )

    if request.method == "POST":
        form = LabOrderUpdateForm(request.POST)

        if form.is_valid():
            order.status = form.cleaned_data["status"]
            order.result = form.cleaned_data["result"]
            order.notes = form.cleaned_data["notes"]

            if order.status == LabTestOrder.Status.COMPLETED:
                order.result_date = timezone.now()

            order.save()

            return redirect(
                "medical_records:lab_orders"
            )

    else:
        form = LabOrderUpdateForm(
            initial={
                "status": order.status,
                "result": order.result,
                "notes": order.notes,
            }
        )

    return render(
        request,
        "medical_records/lab_order_update.html",
        {
            "form": form,
            "order": order,
        },
    )


User = get_user_model()


@login_required
def doctor_patient_lab_reports(request, patient_id):
    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    patient = get_object_or_404(
        User,
        id=patient_id,
        role="PATIENT",
    )

    if not doctor_has_patient_relationship(
        request.user,
        patient,
    ):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    reports = (
        LabTestOrder.objects
        .filter(patient=patient)
        .select_related(
            "patient",
            "doctor",
            "test",
            "consultation",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "medical_records/doctor_patient_lab_reports.html",
        {
            "patient": patient,
            "reports": reports,
        },
    )

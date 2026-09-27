from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render, get_object_or_404
from apps.appointments.services import get_available_slots
from apps.doctors.models import DoctorProfile
from apps.appointments.models import Appointment
from apps.medical_records.models import Prescription
from apps.medical_records.models import (Consultation,Prescription,LabTestOrder,)
from django.shortcuts import render

@login_required
def patient_dashboard(request):
    return render(
        request,
        "patients/dashboard.html",
    )

@login_required
def patient_profile(request):
    return render(
        request,
        "patients/profile.html",
    )
@login_required
def find_doctors(request):

    query = request.GET.get("q", "").strip()

    doctors = DoctorProfile.objects.select_related(
        "user",
        "hospital",
        "department",
    ).all()

    if query:
        doctors = doctors.filter(
            models.Q(
                user__first_name__icontains=query
            )
            | models.Q(
                user__last_name__icontains=query
            )
            | models.Q(
                specialization__icontains=query
            )
            | models.Q(
                department__name__icontains=query
            )
        )

    return render(
        request,
        "patients/find_doctors.html",
        {
            "doctors": doctors,
            "query": query,
        },
    )

@login_required
def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(
        DoctorProfile.objects.select_related(
            "user",
            "hospital",
            "department",
        ),
        id=doctor_id,
    )

    selected_date = request.GET.get("date")

    available_slots = []

    if selected_date:
        try:
            from datetime import datetime

            selected_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d",
            ).date()

            available_slots = get_available_slots(
                doctor=doctor,
                date=selected_date,
            )

        except ValueError:
            selected_date = None

    return render(
        request,
        "patients/doctor_detail.html",
        {
            "doctor": doctor,
            "selected_date": selected_date,
            "available_slots": available_slots,
        },
    )

@login_required
def my_appointments(request):
    appointments = (
        Appointment.objects
        .filter(patient=request.user)
        .select_related(
            "doctor__user",
            "doctor__hospital",
            "doctor__department",
            "department",
        )
        .order_by(
            "-date",
            "-start_time",
        )
    )

    return render(
        request,
        "patients/appointments.html",
        {
            "appointments": appointments,
        },
    )

@login_required
def my_prescriptions(request):

    prescriptions = (
        Prescription.objects
        .filter(
            patient=request.user,
        )
        .select_related(
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
        "patients/prescriptions.html",
        {
            "prescriptions": prescriptions,
        },
    )


@login_required
def my_lab_reports(request):

    reports = (
        LabTestOrder.objects
        .filter(
            patient=request.user,
        )
        .select_related(
            "doctor",
            "test",
            "consultation",
        )
        .order_by(
            "-created_at",
        )
    )

    return render(
        request,
        "patients/lab_reports.html",
        {
            "reports": reports,
        },
    )

@login_required
def medical_history(request):
    consultations = (
        Consultation.objects
        .filter(patient=request.user)
        .select_related("doctor")
        .order_by("-created_at")
    )

    lab_reports = (
        LabTestOrder.objects
        .filter(
            patient=request.user,
        )
        .select_related(
            "doctor",
            "test",
        )
        .order_by(
            "-created_at",
        )
    )

    return render(
        request,
        "patients/medical_history.html",
        {
            "consultations": consultations,
            "lab_reports": lab_reports,
        },
    )
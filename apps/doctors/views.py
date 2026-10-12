from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.appointments.models import Appointment
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render

@login_required
def doctor_dashboard(request):

    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    today = timezone.localdate()
    doctor_appointments = Appointment.objects.filter(doctor__user=request.user)

    return render(
        request,
        "doctors/dashboard.html",
        {
            "today_count": doctor_appointments.filter(date=today).exclude(
                status__in=[Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW]
            ).count(),
            "patient_count": doctor_appointments.values("patient_id").distinct().count(),
            "completed_count": doctor_appointments.filter(
                status=Appointment.Status.COMPLETED
            ).count(),
            "upcoming_count": doctor_appointments.filter(
                date__gte=today,
                status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
            ).count(),
            "today_appointments": doctor_appointments.filter(
                date=today,
                status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
            ).select_related("patient", "department").order_by("start_time"),
        },
    )


@login_required
def doctor_profile(request):

    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    profile = getattr(
        request.user,
        "doctor_profile",
        None,
    )

    return render(
        request,
        "doctors/profile.html",
        {
            "profile": profile,
        },
    )

@login_required
def doctor_appointments(request):
    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    appointments = (
        Appointment.objects
        .filter(
            doctor__user=request.user,
        )
        .select_related(
            "patient",
            "doctor__user",
            "department",
        )
        .order_by(
            "date",
            "start_time",
        )
    )

    return render(
        request,
        "doctors/appointments.html",
        {
            "appointments": appointments,
        },
    )
@login_required
def update_appointment_status(request, appointment_id, status):

    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        doctor__user=request.user,
    )

    if request.method == "POST":

        if (
            appointment.status == Appointment.Status.PENDING
            and status == "CONFIRMED"
        ):
            appointment.status = Appointment.Status.CONFIRMED

        elif (
            appointment.status == Appointment.Status.PENDING
            and status == "CANCELLED"
        ):
            appointment.status = Appointment.Status.CANCELLED

        elif (
            appointment.status == Appointment.Status.CONFIRMED
            and status == "COMPLETED"
        ):
            appointment.status = Appointment.Status.COMPLETED

        elif (
            appointment.status == Appointment.Status.CONFIRMED
            and status == "NO_SHOW"
        ):
            appointment.status = Appointment.Status.NO_SHOW

        appointment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    return redirect("doctors:appointments")

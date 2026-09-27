from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.doctors.models import DoctorProfile

from .forms import AppointmentBookingForm
from .models import Appointment
from .services import get_available_slots


@login_required
def book_appointment(request, doctor_id):

    doctor = get_object_or_404(
        DoctorProfile.objects.select_related(
            "user",
            "hospital",
            "department",
        ),
        id=doctor_id,
    )

    date_string = request.GET.get("date")
    start_time_string = request.GET.get("start_time")
    end_time_string = request.GET.get("end_time")

    if not all(
        [
            date_string,
            start_time_string,
            end_time_string,
        ]
    ):
        return render(
            request,
            "errors/400.html",
            status=400,
        )

    try:
        appointment_date = datetime.strptime(
            date_string,
            "%Y-%m-%d",
        ).date()

        start_time = datetime.strptime(
            start_time_string,
            "%H:%M:%S",
        ).time()

        end_time = datetime.strptime(
            end_time_string,
            "%H:%M:%S",
        ).time()

    except ValueError:

        try:
            start_time = datetime.strptime(
                start_time_string,
                "%H:%M",
            ).time()

            end_time = datetime.strptime(
                end_time_string,
                "%H:%M",
            ).time()

            appointment_date = datetime.strptime(
                date_string,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            return render(
                request,
                "errors/400.html",
                status=400,
            )

    available_slots = get_available_slots(
        doctor=doctor,
        date=appointment_date,
    )

    selected_slot_exists = any(
        slot["start_time"] == start_time
        and slot["end_time"] == end_time
        for slot in available_slots
    )

    if not selected_slot_exists:
        return render(
            request,
            "appointments/slot_unavailable.html",
            {
                "doctor": doctor,
                "date": appointment_date,
            },
            status=409,
        )

    if request.method == "POST":

        form = AppointmentBookingForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                already_booked = Appointment.objects.filter(
                    doctor=doctor,
                    date=appointment_date,
                    start_time=start_time,
                    end_time=end_time,
                    status__in=[
                        Appointment.Status.PENDING,
                        Appointment.Status.CONFIRMED,
                    ],
                ).exists()

                if already_booked:
                    return render(
                        request,
                        "appointments/slot_unavailable.html",
                        {
                            "doctor": doctor,
                            "date": appointment_date,
                        },
                        status=409,
                    )

                Appointment.objects.create(
                    patient=request.user,
                    doctor=doctor,
                    department=doctor.department,
                    date=appointment_date,
                    start_time=start_time,
                    end_time=end_time,
                    status=Appointment.Status.PENDING,
                    reason=form.cleaned_data["reason"],
                    notes=form.cleaned_data["notes"],
                )

            return redirect(
                "patients:appointments"
            )

    else:

        form = AppointmentBookingForm()

    return render(
        request,
        "appointments/book_appointment.html",
        {
            "doctor": doctor,
            "date": appointment_date,
            "start_time": start_time,
            "end_time": end_time,
            "form": form,
        },
    )
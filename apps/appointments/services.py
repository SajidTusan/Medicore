from datetime import datetime, timedelta

from apps.schedule_manager.models import Schedule

from .models import Appointment


def get_available_slots(doctor, date):
    """
    Return available 30-minute appointment slots
    for a doctor on a specific date.
    """

    schedules = Schedule.objects.filter(
        user=doctor.user,
        date=date,
        is_active=True,
        schedule_type=Schedule.ScheduleType.HOSPITAL_DUTY,
    )

    booked_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=date,
        status__in=[
            Appointment.Status.PENDING,
            Appointment.Status.CONFIRMED,
        ],
    )

    booked_times = {
        (appointment.start_time, appointment.end_time)
        for appointment in booked_appointments
    }

    slots = []

    for schedule in schedules:

        current = datetime.combine(
            date,
            schedule.start_time,
        )

        end = datetime.combine(
            date,
            schedule.end_time,
        )

        while current + timedelta(minutes=30) <= end:

            slot_start = current.time()

            slot_end = (
                current + timedelta(minutes=30)
            ).time()

            if (slot_start, slot_end) not in booked_times:

                slots.append(
                    {
                        "start_time": slot_start,
                        "end_time": slot_end,
                    }
                )

            current += timedelta(minutes=30)

    return slots
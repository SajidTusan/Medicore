from django.urls import path

from . import views


app_name = "appointments"


urlpatterns = [
    path(
        "book/<int:doctor_id>/",
        views.book_appointment,
        name="book",
    ),
    path(
    "<int:appointment_id>/cancel/",
    views.cancel_appointment,
    name="cancel",
),
    path(
    "doctor/appointments/",
    views.doctor_appointments,
    name="doctor_appointments",
),

path(
    "doctor/appointments/<int:appointment_id>/confirm/",
    views.confirm_appointment,
    name="confirm_appointment",
),

path(
    "doctor/appointments/<int:appointment_id>/complete/",
    views.complete_appointment,
    name="complete_appointment",
),

path(
    "doctor/appointments/<int:appointment_id>/no-show/",
    views.mark_no_show,
    name="mark_no_show",
),
]
from django.urls import path

from . import views

app_name = "doctors"


urlpatterns = [
    path(
        "",
        views.doctor_dashboard,
        name="dashboard",
    ),
    path(
        "profile/",
        views.doctor_profile,
        name="profile",
    ),
    path(
        "appointments/",
        views.doctor_appointments,
        name="appointments",
    ),
    path(
    "appointments/<int:appointment_id>/<str:status>/",
    views.update_appointment_status,
    name="update_appointment_status",
),
]

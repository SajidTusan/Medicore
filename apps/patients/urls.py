from django.urls import path

from . import views


app_name = "patients"


urlpatterns = [
    path(
        "",
        views.patient_dashboard,
        name="dashboard",
    ),

    path(
        "profile/",
        views.patient_profile,
        name="profile",
    ),

    path(
        "doctors/",
        views.find_doctors,
        name="find_doctors",
    ),

    path(
        "doctors/<int:doctor_id>/",
        views.doctor_detail,
        name="doctor_detail",
    ),

    path(
        "appointments/",
        views.my_appointments,
        name="appointments",
    ),

    path(
        "prescriptions/",
        views.my_prescriptions,
        name="prescriptions",
    ),

    path(
        "lab-reports/",
        views.my_lab_reports,
        name="lab_reports",
    ),
    path(
    "medical-history/",
    views.medical_history,
    name="medical_history",
    ),
    
]
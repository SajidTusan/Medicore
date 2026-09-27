from django.urls import path

from . import views


app_name = "medical_records"


urlpatterns = [
    path(
        "consultation/<int:appointment_id>/",
        views.create_consultation,
        name="create_consultation",
    ),

    path(
        "consultation/view/<int:consultation_id>/",
        views.consultation_detail,
        name="consultation_detail",
    ),
    
    path(
    "prescription/create/<int:consultation_id>/",
    views.create_prescription,
    name="create_prescription",
),

path(
    "prescription/<int:prescription_id>/",
    views.prescription_detail,
    name="prescription_detail",
),
path(
    "lab-order/create/<int:consultation_id>/",
    views.create_lab_order,
    name="create_lab_order",
),
path(
    "lab-orders/",
    views.lab_orders,
    name="lab_orders",
),
path(
    "lab-orders/<int:order_id>/update/",
    views.update_lab_order,
    name="lab_order_update",
),
path(
    "doctor/patient/<int:patient_id>/lab-reports/",
    views.doctor_patient_lab_reports,
    name="doctor_patient_lab_reports",
),
]
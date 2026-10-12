from django.urls import path

from . import views

app_name = "pharmacy"

urlpatterns = [
    path(
        "prescriptions/",
        views.pharmacy_prescriptions,
        name="prescriptions",
    ),
    path(
    "prescriptions/<int:prescription_id>/dispense/",
    views.dispense_prescription,
    name="dispense",
),
]
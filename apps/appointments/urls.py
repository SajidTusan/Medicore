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
]
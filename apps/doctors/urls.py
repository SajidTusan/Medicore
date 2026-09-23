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
]
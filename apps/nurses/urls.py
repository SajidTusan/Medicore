from django.urls import path

from . import views


app_name = "nurses"


urlpatterns = [

    path(
        "",
        views.nurse_dashboard,
        name="dashboard",
    ),

    path(
        "profile/",
        views.nurse_profile,
        name="profile",
    ),

]
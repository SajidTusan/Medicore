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
    
    path(
    "home-care/request/<int:nurse_id>/",
    views.request_home_care,
    name="request_home_care",
),

path(
    "home-care/my-requests/",
    views.my_home_care_requests,
    name="my_home_care_requests",
),

]
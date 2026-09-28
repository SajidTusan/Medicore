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

path(
    "home-care/requests/",
    views.nurse_home_care_requests,
    name="nurse_home_care_requests",
),

path(
    "home-care/requests/<int:request_id>/update/",
    views.update_home_care_request,
    name="update_home_care_request",
),

path(
    "home-care/requests/<int:request_id>/start/",
    views.start_home_care_service,
    name="start_home_care_service",
),

path(
    "home-care/requests/<int:request_id>/complete/",
    views.complete_home_care_service,
    name="complete_home_care_service",
),

path(
    "home-care/requests/<int:request_id>/review/",
    views.review_home_care,
    name="review_home_care",
),

]
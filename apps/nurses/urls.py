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
        views.nurse_requests,
        name="nurse_requests",
    ),

    path(
        "home-care/requests/<int:request_id>/accept/",
        views.accept_home_care_request,
        name="accept_request",
    ),

    path(
        "home-care/requests/<int:request_id>/reject/",
        views.reject_home_care_request,
        name="reject_request",
    ),

    path(
        "home-care/requests/<int:request_id>/start/",
        views.start_home_care_request,
        name="start_request",
    ),

    path(
        "home-care/requests/<int:request_id>/complete/",
        views.complete_home_care_request,
        name="complete_request",
    ),

    path(
        "home-care/requests/<int:request_id>/cancel/",
        views.cancel_home_care_request,
        name="cancel_request",
    ),

    path(
        "home-care/requests/<int:request_id>/review/",
        views.create_home_care_review,
        name="create_review",
    ),
]
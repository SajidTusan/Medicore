from django.urls import path

from . import views


app_name = "schedule_manager"


urlpatterns = [

    path(
        "",
        views.schedule_list,
        name="list",
    ),

    path(
        "add/",
        views.schedule_create,
        name="create",
    ),

    path(
        "<int:pk>/edit/",
        views.schedule_edit,
        name="edit",
    ),

    path(
        "<int:pk>/delete/",
        views.schedule_delete,
        name="delete",
    ),

]
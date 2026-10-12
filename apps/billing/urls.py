from django.urls import path

from . import views


app_name = "billing"


urlpatterns = [
    path(
        "",
        views.bill_list,
        name="bills",
    ),

    path(
        "<int:bill_id>/",
        views.bill_detail,
        name="bill_detail",
    ),

    path(
        "<int:bill_id>/payment/",
        views.record_payment,
        name="record_payment",
    ),
]
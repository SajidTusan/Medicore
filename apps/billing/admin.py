from django.contrib import admin

from .models import Bill, Payment


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        "bill_id",
        "patient",
        "total_amount",
        "paid_amount",
        "status",
        "created_at",
    )

    search_fields = (
        "bill_id",
        "patient__username",
        "patient__public_id",
    )

    list_filter = (
        "status",
        "created_at",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "bill",
        "amount",
        "method",
        "transaction_id",
        "paid_by",
        "paid_at",
    )

    search_fields = (
        "bill__bill_id",
        "transaction_id",
        "paid_by__username",
    )

    list_filter = (
        "method",
        "paid_at",
    )
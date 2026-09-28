from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PaymentForm
from .models import Bill, Payment


@login_required
def bill_list(request):
    if request.user.role not in ["ADMIN", "RECEPTIONIST"]:
        return render(request, "errors/403.html", status=403)

    bills = Bill.objects.select_related("patient").order_by("-created_at")

    return render(
        request,
        "billing/bills.html",
        {
            "bills": bills,
        },
    )


@login_required
def bill_detail(request, bill_id):
    bill = get_object_or_404(
        Bill.objects.select_related("patient"),
        id=bill_id,
    )

    if request.user.role not in [
        "ADMIN",
        "RECEPTIONIST",
        "PATIENT",
    ]:
        return render(request, "errors/403.html", status=403)

    if request.user.role == "PATIENT" and bill.patient != request.user:
        return render(request, "errors/403.html", status=403)

    payments = bill.payments.select_related("paid_by").order_by("-paid_at")
    remaining = bill.total_amount - bill.paid_amount
    return render(
        request,
        "billing/bill_detail.html",
        {
            "bill": bill,
            "payments": payments,
            "remaining": remaining,
        },
    )


@login_required
def record_payment(request, bill_id):
    if request.user.role not in ["ADMIN", "RECEPTIONIST"]:
        return render(request, "errors/403.html", status=403)

    bill = get_object_or_404(Bill, id=bill_id)

    if bill.status in [
        Bill.Status.PAID,
        Bill.Status.CANCELLED,
    ]:
        messages.warning(
            request,
            "This bill cannot receive another payment.",
        )
        return redirect("billing:bill_detail", bill_id=bill.id)

    if request.method == "POST":
        form = PaymentForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                bill = Bill.objects.select_for_update().get(id=bill.id)

                remaining = bill.total_amount - bill.paid_amount
                amount = form.cleaned_data["amount"]

                if amount > remaining:
                    form.add_error(
                        "amount",
                        f"Maximum payable amount is {remaining}.",
                    )
                elif amount <= 0:
                    form.add_error(
                        "amount",
                        "Payment amount must be greater than zero.",
                    )
                else:
                    payment = form.save(commit=False)

                    payment.bill = bill
                    payment.paid_by = request.user
                    payment.save()

                    bill.paid_amount += amount
                    bill.update_status()

                    bill.save(
                        update_fields=[
                            "paid_amount",
                            "status",
                            "updated_at",
                        ]
                    )

                    messages.success(
                        request,
                        f"Payment of {amount} recorded successfully.",
                    )

                    return redirect(
                        "billing:bill_detail",
                        bill_id=bill.id,
                    )

    else:
        form = PaymentForm()

    remaining = bill.total_amount - bill.paid_amount

    return render(
        request,
        "billing/payment_form.html",
        {
            "bill": bill,
            "form": form,
            "remaining": remaining,
        },
    )

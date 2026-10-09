
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def home(request):
    role_routes = {
        "ADMIN": "/admin/",
        "DOCTOR": "/doctors/",
        "NURSE": "/nurses/",
        "PATIENT": "/patients/",
        "LAB": "/medical-records/lab-orders/",
        "PHARMACIST": "/pharmacy/prescriptions/",
        "RECEPTIONIST": "/billing/",
    }

    return redirect(role_routes.get(request.user.role, "/accounts/login/"))

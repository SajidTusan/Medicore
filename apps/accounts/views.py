
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import PatientSignUpForm

def home(request):
    if not request.user.is_authenticated:
        return render(request, "public/home.html")

    role_routes = {
        "ADMIN": "/admin/",
        "DOCTOR": "/doctors/",
        "NURSE": "/nurses/",
        "PATIENT": "/patients/",
        "LAB": "/medical-records/lab-orders/",
        "PHARMACIST": "/pharmacy/prescriptions/",
        "RECEPTIONIST": "/billing/",
    }

    return redirect(role_routes.get(request.user.role, reverse("login")))


def patient_signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = PatientSignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"{reverse('login')}?registered=1")

    return render(request, "accounts/signup.html", {"form": form})

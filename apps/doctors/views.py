from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def doctor_dashboard(request):

    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    return render(
        request,
        "doctors/dashboard.html",
    )


@login_required
def doctor_profile(request):

    if request.user.role != "DOCTOR":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    profile = getattr(
        request.user,
        "doctor_profile",
        None,
    )

    return render(
        request,
        "doctors/profile.html",
        {
            "profile": profile,
        },
    )
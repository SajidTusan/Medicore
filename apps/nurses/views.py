from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def nurse_dashboard(request):

    if request.user.role != "NURSE":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    profile = getattr(
        request.user,
        "nurse_profile",
        None,
    )

    return render(
        request,
        "nurses/dashboard.html",
        {
            "profile": profile,
        },
    )


@login_required
def nurse_profile(request):

    if request.user.role != "NURSE":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    profile = getattr(
        request.user,
        "nurse_profile",
        None,
    )

    return render(
        request,
        "nurses/profile.html",
        {
            "profile": profile,
        },
    )
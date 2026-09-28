from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .forms import HomeCareRequestForm
from .models import NurseProfile, HomeCareRequest
from .services import is_nurse_available

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
    
@login_required
def request_home_care(request, nurse_id):

    if request.user.role != "PATIENT":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    nurse = get_object_or_404(
        NurseProfile.objects
        .select_related("user", "hospital"),
        id=nurse_id,
    )

    if request.method == "POST":

        form = HomeCareRequestForm(request.POST)

        if form.is_valid():

            date = form.cleaned_data["date"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]

            available, message = is_nurse_available(
                nurse=nurse,
                date=date,
                start_time=start_time,
                end_time=end_time,
            )

            if not available:

                form.add_error(
                    None,
                    message,
                )

            else:

                home_care_request = form.save(
                    commit=False
                )

                home_care_request.patient = request.user
                home_care_request.nurse = nurse
                home_care_request.save()

                messages.success(
                    request,
                    "Home-care request submitted successfully.",
                )

                return redirect(
                    "nurses:my_home_care_requests"
                )

    else:

        form = HomeCareRequestForm()

    return render(
        request,
        "nurses/request_home_care.html",
        {
            "nurse": nurse,
            "form": form,
        },
    )

@login_required
def my_home_care_requests(request):

    if request.user.role != "PATIENT":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    requests = (
        HomeCareRequest.objects
        .filter(patient=request.user)
        .select_related(
            "nurse",
            "nurse__user",
            "nurse__hospital",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "nurses/my_home_care_requests.html",
        {
            "requests": requests,
        },
    )
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.notifications.services import create_notification
from .forms import HomeCareRequestForm, HomeCareReviewForm
from .models import HomeCareRequest, HomeCareReview, NurseProfile
from .services import is_nurse_available


@login_required
def nurse_dashboard(request):
    if request.user.role != "NURSE":
        return render(request, "errors/403.html", status=403)

    profile = getattr(request.user, "nurse_profile", None)
    return render(request, "nurses/dashboard.html", {"profile": profile})


@login_required
def nurse_profile(request):
    if request.user.role != "NURSE":
        return render(request, "errors/403.html", status=403)

    profile = getattr(request.user, "nurse_profile", None)
    return render(request, "nurses/profile.html", {"profile": profile})
    

@login_required
def request_home_care(request, nurse_id):
    if request.user.role != "PATIENT":
        return render(request, "errors/403.html", status=403)

    nurse = get_object_or_404(
        NurseProfile.objects.select_related("user", "hospital"),
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
                form.add_error(None, message)
            else:
                home_care_request = form.save(commit=False)
                home_care_request.patient = request.user
                home_care_request.nurse = nurse
                home_care_request.save()

                create_notification(
                    recipient=nurse.user,
                    title="New Home-Care Request",
                    message=(
                        f"Patient {request.user.public_id} has requested "
                        f"home-care service on {date} from {start_time} to {end_time}."
                    ),
                    notification_type="HOME_CARE",
                    link="/nurses/home-care/requests/",
                )

                messages.success(request, "Home-care request submitted successfully.")
                return redirect("nurses:my_home_care_requests")
    else:
        form = HomeCareRequestForm()

    return render(request, "nurses/request_home_care.html", {"nurse": nurse, "form": form})


@login_required
def my_home_care_requests(request):
    if request.user.role != "PATIENT":
        return render(request, "errors/403.html", status=403)

    requests = (
        HomeCareRequest.objects
        .filter(patient=request.user)
        .select_related("nurse", "nurse__user", "nurse__hospital")
        .order_by("-created_at")
    )
    return render(request, "nurses/my_home_care_requests.html", {"requests": requests})


@login_required
def nurse_home_care_requests(request):
    if request.user.role != "NURSE":
        return render(request, "errors/403.html", status=403)

    nurse = get_object_or_404(NurseProfile, user=request.user)
    requests = (
        HomeCareRequest.objects
        .filter(nurse=nurse)
        .select_related("patient", "nurse", "nurse__user")
        .order_by("-created_at")
    )
    return render(request, "nurses/home_care_requests.html", {"requests": requests})


@login_required
def update_home_care_request(request, request_id):
    if request.user.role != "NURSE":
        return render(request, "errors/403.html", status=403)

    nurse = get_object_or_404(NurseProfile, user=request.user)
    home_care_request = get_object_or_404(HomeCareRequest, id=request_id, nurse=nurse)

    if request.method != "POST":
        return redirect("nurses:nurse_home_care_requests")

    action = request.POST.get("action")

    if home_care_request.status != HomeCareRequest.Status.PENDING:
        messages.warning(request, "This request has already been processed.")
        return redirect("nurses:nurse_home_care_requests")

    if action == "accept":
        available, message = is_nurse_available(
            nurse=nurse,
            date=home_care_request.date,
            start_time=home_care_request.start_time,
            end_time=home_care_request.end_time,
            exclude_request_id=home_care_request.id,
        )

        if not available:
            messages.error(request, message)
            return redirect("nurses:nurse_home_care_requests")

        home_care_request.status = HomeCareRequest.Status.ACCEPTED
        home_care_request.save(update_fields=["status", "updated_at"])

        create_notification(
            recipient=home_care_request.patient,
            title="Home-Care Request Accepted",
            message=(
                f"Nurse {nurse.user.public_id} has accepted "
                f"your home-care request for {home_care_request.date}."
            ),
            notification_type="HOME_CARE",
            link="/nurses/home-care/my-requests/",
        )

        messages.success(request, "Home-care request accepted.")

    elif action == "reject":
        home_care_request.status = HomeCareRequest.Status.REJECTED
        home_care_request.save(update_fields=["status", "updated_at"])

        create_notification(
            recipient=home_care_request.patient,
            title="Home-Care Request Rejected",
            message=(
                f"Your home-care request for "
                f"{home_care_request.date} was rejected by the nurse."
            ),
            notification_type="HOME_CARE",
            link="/nurses/home-care/my-requests/",
        )

        messages.success(request, "Home-care request rejected.")
    else:
        messages.error(request, "Invalid action.")

    return redirect("nurses:nurse_home_care_requests")


@login_required
def start_home_care_service(request, request_id):
    if request.user.role != "NURSE":
        return render(request, "errors/403.html", status=403)

    nurse = get_object_or_404(NurseProfile, user=request.user)
    home_care_request = get_object_or_404(HomeCareRequest, id=request_id, nurse=nurse)

    if request.method != "POST":
        return redirect("nurses:nurse_home_care_requests")

    if home_care_request.status != HomeCareRequest.Status.ACCEPTED:
        messages.warning(request, "Only an accepted request can be started.")
        return redirect("nurses:nurse_home_care_requests")

    home_care_request.status = HomeCareRequest.Status.ACTIVE
    home_care_request.save(update_fields=["status", "updated_at"])
    messages.success(request, "Home-care service has been started.")
    return redirect("nurses:nurse_home_care_requests")


@login_required
def complete_home_care_service(request, request_id):
    if request.user.role != "NURSE":
        return render(request, "errors/403.html", status=403)

    nurse = get_object_or_404(NurseProfile, user=request.user)
    home_care_request = get_object_or_404(HomeCareRequest, id=request_id, nurse=nurse)

    if request.method != "POST":
        return redirect("nurses:nurse_home_care_requests")
        
    if home_care_request.status != HomeCareRequest.Status.ACTIVE:
        messages.warning(request, "Only an active service can be completed.")
        return redirect("nurses:nurse_home_care_requests")

    home_care_request.status = HomeCareRequest.Status.COMPLETED
    home_care_request.save(update_fields=["status", "updated_at"])

    create_notification(
        recipient=home_care_request.patient,
        title="Home-Care Service Completed",
        message=f"Your home-care service on {home_care_request.date} has been completed.",
        notification_type="HOME_CARE",
        link="/nurses/home-care/my-requests/",
    )

    messages.success(request, "Home-care service has been completed.")
    return redirect("nurses:nurse_home_care_requests")


@login_required
def review_home_care(request, request_id):
    if request.user.role != "PATIENT":
        return render(request, "errors/403.html", status=403)

    home_care_request = get_object_or_404(
        HomeCareRequest, id=request_id, patient=request.user
    )

    if home_care_request.status != HomeCareRequest.Status.COMPLETED:
        messages.warning(request, "You can only review completed services.")
        return redirect("nurses:my_home_care_requests")

    if hasattr(home_care_request, "review"):
        messages.warning(request, "You have already reviewed this service.")
        return redirect("nurses:my_home_care_requests")

    if request.method == "POST":
        form = HomeCareReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.home_care_request = home_care_request
            review.patient = request.user
            review.nurse = home_care_request.nurse
            review.save()

            create_notification(
                recipient=home_care_request.nurse.user,
                title="New Nurse Review",
                message=f"Patient {request.user.public_id} gave you a {review.rating}/5 rating.",
                notification_type="REVIEW",
                link="/nurses/home-care/requests/",
            )

            messages.success(request, "Review submitted successfully.")
            return redirect("nurses:my_home_care_requests")
    else:
        form = HomeCareReviewForm()


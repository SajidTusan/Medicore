from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.notifications.services import create_notification
from apps.schedule_manager.models import Schedule

from .forms import HomeCareRequestForm, HomeCareReviewForm
from .models import HomeCareRequest, HomeCareReview, NurseProfile
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
    today_duties = Schedule.objects.filter(
        user=request.user,
        date=timezone.localdate(),
        is_active=True,
    ).exclude(schedule_type=Schedule.ScheduleType.LEAVE).select_related(
        "hospital", "department"
    )
    pending_requests = (
        HomeCareRequest.objects.filter(
            nurse=profile,
            status=HomeCareRequest.Status.PENDING,
        ).count()
        if profile
        else 0
    )

    return render(
        request,
        "nurses/dashboard.html",
        {
            "profile": profile,
            "today_duties": today_duties,
            "pending_requests": pending_requests,
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
        NurseProfile.objects.select_related(
            "user",
            "hospital",
        ),
        id=nurse_id,
    )

    if request.method == "POST":

        form = HomeCareRequestForm(request.POST)

        if form.is_valid():

            date = form.cleaned_data["date"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]

            available, reason = is_nurse_available(
                nurse=nurse,
                date=date,
                start_time=start_time,
                end_time=end_time,
            )

            if not available:

                form.add_error(
                    None,
                    reason,
                )

            else:

                home_care_request = form.save(
                    commit=False
                )

                home_care_request.patient = request.user
                home_care_request.nurse = nurse

                home_care_request.save()

                create_notification(
                    recipient=nurse.user,
                    title="New Home-Care Request",
                    message=(
                        f"Patient {request.user.public_id} "
                        f"has requested home-care service "
                        f"on {date} from {start_time} "
                        f"to {end_time}."
                    ),
                    notification_type="HOME_CARE",
                    link="/nurses/home-care/requests/",
                )

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


@login_required
def nurse_requests(request):

    if request.user.role != "NURSE":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    nurse = get_object_or_404(
        NurseProfile,
        user=request.user,
    )

    requests = (
        HomeCareRequest.objects
        .filter(nurse=nurse)
        .select_related(
            "patient",
            "nurse",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "nurses/home_care_requests.html",
        {
            "requests": requests,
        },
    )


@login_required
def accept_home_care_request(request, request_id):

    if request.user.role != "NURSE":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    if request.method != "POST":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    nurse = get_object_or_404(
        NurseProfile,
        user=request.user,
    )

    with transaction.atomic():

        home_request = get_object_or_404(
            HomeCareRequest.objects.select_for_update(),
            id=request_id,
            nurse=nurse,
        )

        if home_request.status != HomeCareRequest.Status.PENDING:

            messages.warning(
                request,
                "This request has already been processed.",
            )

            return redirect(
                "nurses:nurse_requests"
            )

        available, reason = is_nurse_available(
            nurse=nurse,
            date=home_request.date,
            start_time=home_request.start_time,
            end_time=home_request.end_time,
            exclude_request_id=home_request.id,
        )

        if not available:

            messages.error(
                request,
                reason,
            )

            return redirect(
                "nurses:nurse_requests"
            )

        home_request.status = (
            HomeCareRequest.Status.ACCEPTED
        )

        home_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        create_notification(
            recipient=home_request.patient,
            title="Home-Care Request Accepted",
            message=(
                f"Nurse {nurse.user.public_id} "
                f"has accepted your home-care request "
                f"for {home_request.date}."
            ),
            notification_type="HOME_CARE",
            link="/nurses/home-care/my-requests/",
        )

    messages.success(
        request,
        "Home-care request accepted successfully.",
    )

    return redirect(
        "nurses:nurse_requests"
    )


@login_required
def reject_home_care_request(request, request_id):

    if request.user.role != "NURSE":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    if request.method != "POST":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    nurse = get_object_or_404(
        NurseProfile,
        user=request.user,
    )

    home_request = get_object_or_404(
        HomeCareRequest,
        id=request_id,
        nurse=nurse,
    )

    if home_request.status != HomeCareRequest.Status.PENDING:

        messages.warning(
            request,
            "This request has already been processed.",
        )

        return redirect(
            "nurses:nurse_requests"
        )

    home_request.status = (
        HomeCareRequest.Status.REJECTED
    )

    home_request.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    create_notification(
        recipient=home_request.patient,
        title="Home-Care Request Rejected",
        message=(
            f"Your home-care request for "
            f"{home_request.date} was rejected "
            f"by the nurse."
        ),
        notification_type="HOME_CARE",
        link="/nurses/home-care/my-requests/",
    )

    messages.success(
        request,
        "Home-care request rejected.",
    )

    return redirect(
        "nurses:nurse_requests"
    )


@login_required
def start_home_care_request(request, request_id):

    if request.user.role != "NURSE":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    if request.method != "POST":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    nurse = get_object_or_404(
        NurseProfile,
        user=request.user,
    )

    home_request = get_object_or_404(
        HomeCareRequest,
        id=request_id,
        nurse=nurse,
    )

    if home_request.status != HomeCareRequest.Status.ACCEPTED:

        return render(
            request,
            "errors/400.html",
            status=400,
        )

    home_request.status = (
        HomeCareRequest.Status.ACTIVE
    )

    home_request.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    create_notification(
        recipient=home_request.patient,
        title="Home-Care Service Started",
        message=(
            f"Your home-care service for "
            f"{home_request.date} has started."
        ),
        notification_type="HOME_CARE",
        link="/nurses/home-care/my-requests/",
    )

    messages.success(
        request,
        "Home-care service started.",
    )

    return redirect(
        "nurses:nurse_requests"
    )


@login_required
def complete_home_care_request(request, request_id):

    if request.user.role != "NURSE":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    if request.method != "POST":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    nurse = get_object_or_404(
        NurseProfile,
        user=request.user,
    )

    home_request = get_object_or_404(
        HomeCareRequest,
        id=request_id,
        nurse=nurse,
    )

    if home_request.status != HomeCareRequest.Status.ACTIVE:

        return render(
            request,
            "errors/400.html",
            status=400,
        )

    home_request.status = (
        HomeCareRequest.Status.COMPLETED
    )

    home_request.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    create_notification(
        recipient=home_request.patient,
        title="Home-Care Service Completed",
        message=(
            f"Your home-care service for "
            f"{home_request.date} has been completed."
        ),
        notification_type="HOME_CARE",
        link="/nurses/home-care/my-requests/",
    )

    messages.success(
        request,
        "Home-care service completed.",
    )

    return redirect(
        "nurses:nurse_requests"
    )


@login_required
def cancel_home_care_request(request, request_id):

    if request.user.role != "PATIENT":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    if request.method != "POST":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    home_request = get_object_or_404(
        HomeCareRequest,
        id=request_id,
        patient=request.user,
    )

    if home_request.status not in [
        HomeCareRequest.Status.PENDING,
        HomeCareRequest.Status.ACCEPTED,
    ]:

        return render(
            request,
            "errors/400.html",
            status=400,
        )

    home_request.status = (
        HomeCareRequest.Status.CANCELLED
    )

    home_request.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    create_notification(
        recipient=home_request.nurse.user,
        title="Home-Care Request Cancelled",
        message=(
            f"Home-care request for "
            f"{home_request.date} was cancelled "
            f"by the patient."
        ),
        notification_type="HOME_CARE",
        link="/nurses/home-care/requests/",
    )

    messages.success(
        request,
        "Home-care request cancelled.",
    )

    return redirect(
        "nurses:my_home_care_requests"
    )


@login_required
def create_home_care_review(request, request_id):

    if request.user.role != "PATIENT":
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    home_request = get_object_or_404(
        HomeCareRequest.objects.select_related(
            "nurse",
        ),
        id=request_id,
        patient=request.user,
        status=HomeCareRequest.Status.COMPLETED,
    )

    # Prevent duplicate review
    if hasattr(home_request, "review"):

        messages.warning(
            request,
            "You have already reviewed this service.",
        )

        return redirect(
            "nurses:my_home_care_requests"
        )

    if request.method == "POST":

        form = HomeCareReviewForm(
            request.POST
        )

        if form.is_valid():

            review = form.save(
                commit=False
            )

            review.request = home_request
            review.patient = request.user
            review.nurse = home_request.nurse

            review.save()

            # Update nurse rating
            nurse = home_request.nurse

            reviews = HomeCareReview.objects.filter(
                nurse=nurse
            )

            nurse.total_reviews = reviews.count()

            nurse.rating = (
                reviews.aggregate(
                    average=Avg("rating")
                )["average"]
                or 0
            )

            nurse.save(
                update_fields=[
                    "rating",
                    "total_reviews",
                    "updated_at",
                ]
            )

            create_notification(
                recipient=nurse.user,
                title="New Nurse Review",
                message=(
                    f"Patient {request.user.public_id} "
                    f"gave you a {review.rating}/5 rating."
                ),
                notification_type="REVIEW",
                link="/nurses/home-care/requests/",
            )

            messages.success(
                request,
                "Your review has been submitted.",
            )

            return redirect(
                "nurses:my_home_care_requests"
            )

    else:

        form = HomeCareReviewForm()

    return render(
        request,
        "nurses/review_home_care.html",
        {
            "form": form,
            "home_care_request": home_request,
        },
    )
    

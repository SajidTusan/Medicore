from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ScheduleForm
from .models import Schedule
from .services import (
    create_schedule,
    has_schedule_conflict,
)


def is_staff_member(user):
    return user.role in ["DOCTOR", "NURSE"]


@login_required
def schedule_list(request):

    if not is_staff_member(request.user):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    schedules = Schedule.objects.filter(
        user=request.user,
        is_active=True,
    ).select_related(
        "hospital",
        "department",
    )

    return render(
        request,
        "schedule_manager/schedule_list.html",
        {
            "schedules": schedules,
        },
    )


@login_required
def schedule_create(request):

    if not is_staff_member(request.user):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    if request.method == "POST":

        form = ScheduleForm(request.POST)

        if form.is_valid():

            date = form.cleaned_data["date"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]
            schedule_type = form.cleaned_data["schedule_type"]
            notes = form.cleaned_data["notes"]

            if (
                request.user.role == "DOCTOR"
                and schedule_type == Schedule.ScheduleType.HOME_CARE
            ):
                form.add_error(
                    "schedule_type",
                    "Doctors cannot create home-care schedules.",
                )

            elif (
                has_schedule_conflict(
                    user=request.user,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                )
            ):
                form.add_error(
                    None,
                    "This schedule conflicts with an existing schedule.",
                )

            else:

                hospital = None
                department = None

                if request.user.role == "DOCTOR":

                    profile = getattr(
                        request.user,
                        "doctor_profile",
                        None,
                    )

                else:

                    profile = getattr(
                        request.user,
                        "nurse_profile",
                        None,
                    )

                if profile:

                    hospital = profile.hospital
                    department = profile.department

                create_schedule(
                    user=request.user,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    schedule_type=schedule_type,
                    hospital=hospital,
                    department=department,
                    notes=notes,
                )

                return redirect(
                    "schedule_manager:list"
                )

    else:

        form = ScheduleForm()

    return render(
        request,
        "schedule_manager/schedule_form.html",
        {
            "form": form,
            "page_title": "Add Schedule",
        },
    )


@login_required
def schedule_edit(request, pk):

    if not is_staff_member(request.user):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    schedule = get_object_or_404(
        Schedule,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        form = ScheduleForm(
            request.POST,
            instance=schedule,
        )

        if form.is_valid():

            date = form.cleaned_data["date"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]

            if has_schedule_conflict(
                user=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
                exclude_id=schedule.id,
            ):
                form.add_error(
                    None,
                    "This schedule conflicts with another schedule.",
                )

            else:

                schedule.date = date
                schedule.start_time = start_time
                schedule.end_time = end_time
                schedule.schedule_type = form.cleaned_data[
                    "schedule_type"
                ]
                schedule.notes = form.cleaned_data["notes"]

                schedule.save()

                return redirect(
                    "schedule_manager:list"
                )

    else:

        form = ScheduleForm(
            instance=schedule,
        )

    return render(
        request,
        "schedule_manager/schedule_form.html",
        {
            "form": form,
            "page_title": "Edit Schedule",
            "schedule": schedule,
        },
    )


@login_required
def schedule_delete(request, pk):

    if not is_staff_member(request.user):
        return render(
            request,
            "errors/403.html",
            status=403,
        )

    schedule = get_object_or_404(
        Schedule,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        schedule.is_active = False
        schedule.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return redirect(
            "schedule_manager:list"
        )

    return render(
        request,
        "schedule_manager/schedule_confirm_delete.html",
        {
            "schedule": schedule,
        },
    )
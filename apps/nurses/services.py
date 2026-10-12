from apps.schedule_manager.models import Schedule

from .models import HomeCareAvailability, HomeCareRequest


def is_nurse_available(
    nurse,
    date,
    start_time,
    end_time,
    exclude_request_id=None,
):
    """
    Check whether a nurse is available for home-care
    on a specific date and time.
    """

    day_name = date.strftime("%A").upper()

    availability_exists = HomeCareAvailability.objects.filter(
        nurse=nurse,
        day=day_name,
        is_active=True,
        start_time__lte=start_time,
        end_time__gte=end_time,
    ).exists()

    if not availability_exists:
        return False, "Nurse is not available during this time."

    hospital_conflict = Schedule.objects.filter(
    user=nurse.user,
    date=date,
    is_active=True,
    schedule_type=Schedule.ScheduleType.HOSPITAL_DUTY,
    start_time__lt=end_time,
    end_time__gt=start_time,
        ).exists()

    if hospital_conflict:
        return False, "This time conflicts with the nurse's hospital duty."


    leave_conflict = Schedule.objects.filter(
    user=nurse.user,
    date=date,
    is_active=True,
    schedule_type=Schedule.ScheduleType.LEAVE,
    start_time__lt=end_time,
    end_time__gt=start_time,
    ).exists()

    if leave_conflict:
        return False, "Nurse is on leave during this time."

    existing_requests = HomeCareRequest.objects.filter(
        nurse=nurse,
        date=date,
        status__in=[
            HomeCareRequest.Status.PENDING,
            HomeCareRequest.Status.ACCEPTED,
            HomeCareRequest.Status.ACTIVE,
        ],
        start_time__lt=end_time,
        end_time__gt=start_time,
    )

    if exclude_request_id:
        existing_requests = existing_requests.exclude(
            id=exclude_request_id
        )

    if existing_requests.exists():
        return False, "Nurse already has another home-care request during this time."

    return True, ""
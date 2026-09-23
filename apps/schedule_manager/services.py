from .models import Schedule


def validate_schedule_time(
    start_time,
    end_time,
):
    """
    Make sure start time is before end time.
    """

    if start_time >= end_time:
        raise ValueError(
            "Start time must be earlier than end time."
        )


def has_schedule_conflict(
    user,
    date,
    start_time,
    end_time,
    exclude_id=None,
):
    """
    Check whether the user already has
    another active schedule at the same time.
    """

    queryset = Schedule.objects.filter(
        user=user,
        date=date,
        is_active=True,
        start_time__lt=end_time,
        end_time__gt=start_time,
    )

    if exclude_id:
        queryset = queryset.exclude(
            id=exclude_id,
        )

    return queryset.exists()


def create_schedule(
    *,
    user,
    date,
    start_time,
    end_time,
    schedule_type,
    hospital=None,
    department=None,
    notes="",
):
    """
    Validate and create a new schedule.
    """

    validate_schedule_time(
        start_time,
        end_time,
    )

    if has_schedule_conflict(
        user=user,
        date=date,
        start_time=start_time,
        end_time=end_time,
    ):
        raise ValueError(
            "This schedule conflicts with an existing schedule."
        )

    return Schedule.objects.create(
        user=user,
        hospital=hospital,
        department=department,
        date=date,
        start_time=start_time,
        end_time=end_time,
        schedule_type=schedule_type,
        notes=notes,
    )
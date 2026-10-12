from datetime import date, time

from django.test import TestCase

from apps.accounts.models import User
from apps.schedule_manager.models import Schedule
from apps.schedule_manager.services import (
    create_schedule,
    has_schedule_conflict,
)

class ScheduleServiceTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="schedule_test_user",
            password="testpass123",
            role="NURSE",
        )

        self.date = date(
            2026,
            9,
            25,
        )


    def test_create_schedule(self):

        schedule = create_schedule(
            user=self.user,
            date=self.date,
            start_time=time(8, 0),
            end_time=time(16, 0),
            schedule_type=Schedule.ScheduleType.HOSPITAL_DUTY,
        )

        self.assertIsNotNone(
            schedule.id
        )

        self.assertEqual(
            schedule.user,
            self.user,
        )


    def test_overlapping_schedule_is_detected(self):

        create_schedule(
            user=self.user,
            date=self.date,
            start_time=time(8, 0),
            end_time=time(16, 0),
            schedule_type=Schedule.ScheduleType.HOSPITAL_DUTY,
        )

        conflict = has_schedule_conflict(
            user=self.user,
            date=self.date,
            start_time=time(14, 0),
            end_time=time(18, 0),
        )

        self.assertTrue(
            conflict
        )


    def test_non_overlapping_schedule_is_allowed(self):

        create_schedule(
            user=self.user,
            date=self.date,
            start_time=time(8, 0),
            end_time=time(16, 0),
            schedule_type=Schedule.ScheduleType.HOSPITAL_DUTY,
        )

        conflict = has_schedule_conflict(
            user=self.user,
            date=self.date,
            start_time=time(16, 0),
            end_time=time(18, 0),
        )

        self.assertFalse(
            conflict
        )


    def test_invalid_time_is_rejected(self):

        with self.assertRaises(
            ValueError
        ):

            create_schedule(
                user=self.user,
                date=self.date,
                start_time=time(18, 0),
                end_time=time(10, 0),
                schedule_type=Schedule.ScheduleType.HOME_CARE,
            )
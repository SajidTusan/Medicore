from django import forms

from .models import Schedule


class ScheduleForm(forms.ModelForm):

    class Meta:
        model = Schedule

        fields = [
            "hospital",
            "department",
            "date",
            "start_time",
            "end_time",
            "schedule_type",
            "is_active",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "start_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),
            "end_time": forms.TimeInput(
                attrs={
                    "type": "time",
                }
            ),
        }
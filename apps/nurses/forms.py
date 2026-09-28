from django import forms

from .models import HomeCareRequest


class HomeCareRequestForm(forms.ModelForm):

    class Meta:
        model = HomeCareRequest

        fields = [
            "date",
            "start_time",
            "end_time",
            "location",
            "required_skills",
            "patient_notes",
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
            "location": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Home-care location...",
                }
            ),
            "required_skills": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Example: Elderly Care, Injection, Wound Care",
                }
            ),
            "patient_notes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Additional information...",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:

            if start_time >= end_time:
                raise forms.ValidationError(
                    "End time must be later than start time."
                )

        return cleaned_data
from django import forms
from django.utils import timezone
from .models import HomeCareRequest, HomeCareReview


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
                    "placeholder": (
                        "Example: Elderly Care, Injection, Wound Care"
                    ),
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

            date = cleaned_data.get("date")
            start_time = cleaned_data.get("start_time")
            end_time = cleaned_data.get("end_time")

            if date and date < timezone.localdate():
                raise forms.ValidationError(
                    "Home-care date cannot be in the past."
                )

            if start_time and end_time:
                if start_time >= end_time:
                    raise forms.ValidationError(
                        "End time must be later than start time."
                    )

            return cleaned_data


class HomeCareReviewForm(forms.ModelForm):

    class Meta:
        model = HomeCareReview

        fields = [
            "rating",
            "comment",
        ]

        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "step": 1,
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Share your experience...",
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")

        if rating is None:
            raise forms.ValidationError(
                "Rating is required."
            )

        if rating < 1 or rating > 5:
            raise forms.ValidationError(
                "Rating must be between 1 and 5."
            )

        return rating
from django import forms


class AppointmentBookingForm(forms.Form):

    reason = forms.CharField(
        label="Reason for Visit",
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Briefly describe why you want to consult the doctor.",
            }
        ),
        required=False,
    )

    notes = forms.CharField(
        label="Additional Notes",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Any additional information...",
            }
        ),
        required=False,
    )
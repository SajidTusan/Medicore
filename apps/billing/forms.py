from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = [
            "amount",
            "method",
            "transaction_id",
            "notes",
        ]

        widgets = {
            "amount": forms.NumberInput(
                attrs={
                    "min": "1",
                    "step": "0.01",
                }
            ),
            "transaction_id": forms.TextInput(
                attrs={
                    "placeholder": "Transaction ID (if applicable)",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Payment notes...",
                }
            ),
        }
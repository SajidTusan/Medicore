from django import forms
from django.db.models import Q

from .models import Medicine


class DispenseMedicineForm(forms.Form):
    medicine = forms.ModelChoiceField(
        queryset=Medicine.objects.none(),
        label="Medicine",
    )

    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity",
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Pharmacy notes...",
        }),
    )

    def __init__(self, *args, prescription=None, **kwargs):
        super().__init__(*args, **kwargs)

        if prescription is not None:
            prescribed_names = prescription.medicines.values_list(
                "medicine_name",
                flat=True,
            )

            query = Q(pk__in=[])

            for name in prescribed_names:
                query |= Q(name__iexact=name.strip())

            self.fields["medicine"].queryset = (
                Medicine.objects
                .filter(query, is_active=True)
                .order_by("name")
            )
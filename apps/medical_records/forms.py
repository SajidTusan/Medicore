from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseFormSet, formset_factory
from .models import Consultation, LabTest
from .models import (Consultation,Prescription,PrescriptionMedicine,LabTest,LabTestOrder,)

class ConsultationForm(forms.ModelForm):

    class Meta:
        model = Consultation
        fields = [
            "chief_complaint",
            "symptoms",
            "diagnosis",
            "clinical_notes",
            "follow_up_date",
        ]
        widgets = {
            "chief_complaint": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Main complaint of the patient...",
                }
            ),
            "symptoms": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Patient symptoms...",
                }
            ),
            "diagnosis": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Doctor's diagnosis...",
                }
            ),
            "clinical_notes": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Clinical notes...",
                }
            ),
            "follow_up_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }


class PrescriptionForm(forms.Form):
    advice = forms.CharField(
        label="General Advice",
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "General advice for the patient...",
            }
        ),
        required=False,
    )

    tests_advised = forms.CharField(
        label="Tests Advised",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Example: CBC, Blood Sugar, X-Ray...",
            }
        ),
        required=False,
    )

    follow_up_date = forms.DateField(
        label="Follow-up Date",
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
            }
        ),
    )


class PrescriptionMedicineForm(forms.Form):
    medicine_name = forms.CharField(
        label="Medicine Name",
        max_length=200,
    )

    dosage = forms.CharField(
        label="Dosage",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Example: 500 mg",
            }
        ),
    )

    frequency = forms.CharField(
        label="Frequency",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Example: 1+1+1",
            }
        ),
    )

    duration = forms.CharField(
        label="Duration",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Example: 5 days",
            }
        ),
    )

    instructions = forms.CharField(
        label="Instructions",
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "placeholder": "Example: After meal",
            }
        ),
        required=False,
    )


class BasePrescriptionMedicineFormSet(BaseFormSet):

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        medicine_count = 0

        for form in self.cleaned_data:
            if not form:
                continue

            if form.get("DELETE"):
                continue

            if form.get("medicine_name"):
                medicine_count += 1

        if medicine_count == 0:
            raise ValidationError("At least one medicine is required.")


PrescriptionMedicineFormSet = formset_factory(
    PrescriptionMedicineForm,
    formset=BasePrescriptionMedicineFormSet,
    extra=1,
    can_delete=True,
)


class LabTestOrderForm(forms.Form):
    test = forms.ModelChoiceField(
        queryset=LabTest.objects.filter(is_active=True).order_by("name"),
        label="Select Laboratory Test",
        empty_label="Select a test",
    )

    notes = forms.CharField(
        label="Notes",
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": "Any instruction for laboratory staff...",
            }
        ),
        required=False,
    )
class LabOrderUpdateForm(forms.Form):

    status = forms.ChoiceField(
        choices=LabTestOrder.Status.choices,
        label="Status",
    )

    result = forms.CharField(
        label="Test Result",
        widget=forms.Textarea(
            attrs={
                "rows": 8,
                "placeholder": "Enter laboratory test result...",
            }
        ),
        required=False,
    )

    notes = forms.CharField(
        label="Laboratory Notes",
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Additional laboratory notes...",
            }
        ),
        required=False,
    )
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User


class PatientSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            from apps.patients.models import PatientProfile

            PatientProfile.objects.get_or_create(user=user)
        return user


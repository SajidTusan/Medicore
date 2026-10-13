from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

from .models import User


class PatientSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            self.username_suggestions = self._username_suggestions(username)
            raise ValidationError(
                "That username is already taken. Choose one of the suggestions below or enter a different username."
            )
        return username

    @staticmethod
    def _username_suggestions(username):
        suggestions = []
        for suffix in ("_1", "_2", "_3", "1", "2"):
            candidate = f"{username[:150 - len(suffix)]}{suffix}"
            if not User.objects.filter(username__iexact=candidate).exists():
                suggestions.append(candidate)
            if len(suggestions) == 3:
                break
        return suggestions

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            from apps.patients.models import PatientProfile

            PatientProfile.objects.get_or_create(user=user)
        return user


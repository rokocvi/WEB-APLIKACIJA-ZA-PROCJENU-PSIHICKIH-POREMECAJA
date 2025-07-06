from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import DateInput
from django.core.exceptions import ValidationError
from mindapp.models import Lijecnik  

USER_TYPE_CHOICES = (
    ('user', 'Korisnik'),
    ('lijecnik', 'Liječnik'),
)

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Ime")
    last_name = forms.CharField(max_length=30, required=True, label="Prezime")
    datum_rodenja = forms.DateField(
        required=True,
        widget=DateInput(attrs={'type': 'date'}),
        label="Datum rođenja"
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'datum_rodenja', 'user_type']

class LijecnikForm(forms.ModelForm):
    class Meta:
        model = Lijecnik
        fields = ['strucnost', 'verifikacijski_dokument']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class LijecnikUpdateForm(forms.ModelForm):
    class Meta:
        model = Lijecnik
        exclude = ['user', 'odobren', 'verifikacijski_dokument'] 


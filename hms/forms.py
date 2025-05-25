from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        exclude = ('status', 'user', 'dob', 'doj')

# email


class ConfirmationForm(forms.Form):
    email = forms.EmailField(label="Enter Email to Confirm Booking")
# email

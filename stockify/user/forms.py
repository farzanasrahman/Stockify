from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from .models import *

class CreateUserForm(UserCreationForm):
    """
    Form for creating a new user.
    """
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.CharField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 
                  'password1', 'password2']


class ProfileForm(ModelForm):
    """
    Form for creating/editing a user profile.
    """
    class Meta:
        model = Profile
        fields = ['address', 'phone_number', 'bio', 'balance', 'image']
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

class LoginForm(AuthenticationForm):
    """
    A form for user login.

    Inherits from Django's `AuthenticationForm` and adds some customization.

    Attributes:
    - `username`: The username field with autofocus and a custom CSS class.
    - `password`: The password field with a custom label, non-stripped, and a custom CSS class.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'})
    )

class UserUpdateForm(forms.ModelForm):
    """
        A form for updating user information.

        Inherits from Django's `ModelForm` and customizes the fields.

        Attributes:
        - `first_name`: A field for the user's first name.
        - `last_name`: A field for the user's last name.
        - `email`: A field for the user's email address.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class UpdateProfileForm(forms.ModelForm):
    """
    A form for updating a user's profile.

    Inherits from Django's `ModelForm` and customizes the fields.

    Attributes:
    - `phone_number`: A field for the user's phone number.
    - `address`: A field for the user's address.
    - `bio`: A field for the user's bio.
    - `balance`: A field for the user's balance.
    - `image`: A field for the user's image.
    """
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'bio', 'balance', 'image']
from django import forms
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'currency']

    def clean_email(self):
        '''
        Verify email is available.
        '''
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email)
        if qs.exists():
            raise ValidationError("An account with this email already exists")
        return email

    def clean_password2(self):
        '''
        Verify both passwords match.
        '''
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        try:
            validate_password(password1, self.instance)
        except ValidationError as error:
            self.add_error('password1', error)

        return password2

    def save(self, commit=True):
        if commit:
            user = CustomUser.objects.create_user(email=self.cleaned_data.get('email'),username=self.cleaned_data.get('username'),first_name=self.cleaned_data.get('first_name'),last_name=self.cleaned_data.get('last_name'),currency=self.cleaned_data.get('currency'),password=self.cleaned_data.get('password2'))
            return user


class CustomUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'currency', 'password', 'is_active', 'is_admin']

    def clean_email(self):
        '''
        Verify email is available.
        '''
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email


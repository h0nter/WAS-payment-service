from django import forms

from payapp.utils import convert_currency
from .models import CustomUser
from payapp.models import Balance
from payapp.constants import Currency
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
            user = CustomUser.objects.create_user(email=self.cleaned_data.get('email'),
                                                  username=self.cleaned_data.get('username'),
                                                  first_name=self.cleaned_data.get('first_name'),
                                                  last_name=self.cleaned_data.get('last_name'),
                                                  currency=self.cleaned_data.get('currency'),
                                                  password=self.cleaned_data.get('password2'))

            # Only non admin users can have balance
            if not user.is_admin:

                # Assign the user equivalent of 1000 GBP in their selected currency
                gbp_amount = 1000

                converted_amount, conversion_success = convert_currency(Currency.GBP, user.currency, gbp_amount)

                # Handle conversion error
                if not conversion_success:
                    raise ValueError(
                        "There was a problem setting up an account with your selected currency. Please try again later.")

                Balance.objects.create(user=user, currency=user.currency, amount=converted_amount)

            return user

    def save_m2m(self):
        CustomUser.objects.assign_permission_groups(self.user)


# Administrator user creation form
class CustomUserCreationFormAdmin(forms.ModelForm):
    user = None
    is_admin = forms.BooleanField(label='Administrator', widget=forms.CheckboxInput(
        attrs={'readonly': 'readonly', 'checked': True}
    ))

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'is_admin']

    def clean_email(self):
        '''
        Verify email is available.
        '''
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email)
        if qs.exists():
            raise ValidationError("An account with this email already exists")
        return email

    def save(self, commit=True):
        if commit:
            self.user = CustomUser.objects.create_user(email=self.cleaned_data.get('email'),
                                                       username=self.cleaned_data.get('username'),
                                                       first_name=self.cleaned_data.get('first_name'),
                                                       last_name=self.cleaned_data.get('last_name'),
                                                       is_admin=self.cleaned_data.get('is_admin'))
        else:
            self.user = CustomUser.objects.create_user_without_save(email=self.cleaned_data.get('email'),
                                                                    username=self.cleaned_data.get('username'),
                                                                    first_name=self.cleaned_data.get('first_name'),
                                                                    last_name=self.cleaned_data.get('last_name'),
                                                                    is_admin=self.cleaned_data.get('is_admin'))
        return self.user

    def save_m2m(self):
        CustomUser.objects.assign_permission_groups(self.user)


class CustomUserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'currency', 'password', 'is_active', 'is_admin',
                  'change_password']

    def clean_email(self):
        '''
        Verify email is available.
        '''
        email = self.cleaned_data.get('email')

        # Check if the provided email address is not used by another user, except of the user themselves
        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)

        # Skip the qs length check as emails are unique -> length == 1
        if qs.exists():
            raise forms.ValidationError("An account is already registered with this email")

        return email

    def clean_username(self):
        '''
        Verify username is available.
        '''
        username = self.cleaned_data.get('username')

        # Check if the provided email address is not used by another user, except of the user themselves
        qs = CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk)

        # Skip the qs length check as emails are unique -> length == 1
        if qs.exists():
            raise forms.ValidationError("This username isn't available")

        return username

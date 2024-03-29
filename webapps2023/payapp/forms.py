from django import forms
from .models import BalanceTransfer, Balance, PaymentRequest
import payapp.constants as constants
from .utils import convert_currency
from decimal import Decimal
from register.models import CustomUser


class BalanceTransferForm(forms.ModelForm):
    recipient_email = forms.EmailField(
        label='Send to:',
        widget=forms.TextInput(attrs={'placeholder': 'example@email.com'})
    )

    class Meta:
        model = BalanceTransfer
        fields = ['recipient_email', 'amount', 'currency', 'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BalanceTransferForm, self).__init__(*args, **kwargs)
        # self.fields['currency'] = forms.CharField(max_length=3, disabled=True,
        #                                           initial=self.request.user.currency)

    def clean_recipient_email(self):
        '''
        Make sure the recipient exists
        '''
        email = self.cleaned_data.get('recipient_email')

        # Check if the sender and recipient aren't the same
        if self.request is not None:
            user = self.request.user

            if user is not None:
                sender_email = user.email

                if sender_email == email:
                    raise forms.ValidationError("You can't send a payment to yourself")
        else:
            raise forms.ValidationError("There was a problem processing your request, please try again.")

        # Check that the recipient exists and is not an administrator
        qs = CustomUser.objects.filter(email=email, is_admin=False).exclude(pk=self.instance.pk)

        if not qs.exists():
            raise forms.ValidationError("A recipient with the given email address doesn't exist")

        return email

    def clean(self):
        '''
        Make sure the amount is not zero and user has enough money for this transaction
        '''

        amount = self.cleaned_data.get('amount')

        if amount <= 0:
            raise forms.ValidationError("The amount must be greater than 0.00")

        if amount > constants.MAX_AMOUNT:
            raise forms.ValidationError(f'The transferred amount cannot exceed {constants.MAX_AMOUNT}')

        if self.request is not None:
            user = self.request.user

            if user is not None:

                balance = Balance.objects.get(user=user)

                currency = self.cleaned_data.get('currency')

                req_amount, conversion_success = convert_currency(currency, user.currency, amount)

                # Handle conversion error
                if not conversion_success:
                    raise forms.ValidationError("There was a problem processing your request, please try again.")

                if balance and req_amount > balance.amount:
                    raise forms.ValidationError("Insufficient funds to complete the transfer.")

                return self.cleaned_data

        raise forms.ValidationError("There was a problem processing your request, please try again.")

    def save(self, commit=True):
        if self.request is not None:
            user = self.request.user

            if user is not None:
                sender_email = user.email

                if commit:
                    bt = BalanceTransfer.objects.create(sender_email=sender_email,
                                                        recipient_email=self.cleaned_data.get('recipient_email'),
                                                        currency=self.cleaned_data.get('currency'),
                                                        amount=self.cleaned_data.get('amount'),
                                                        description=self.cleaned_data.get('description'))
                    return bt

        raise forms.ValidationError("There was a problem processing your request, please try again.")


class PaymentRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = ['sender_email', 'amount', 'currency', 'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.payment_request = kwargs.pop('payment_request', None)
        super(PaymentRequestUpdateForm, self).__init__(*args, **kwargs)
        self.fields['sender_email'] = forms.EmailField(disabled=True,
                                                       initial=self.payment_request.sender_email)
        self.fields['amount'] = forms.DecimalField(disabled=True,
                                                   initial=self.payment_request.amount,
                                                   decimal_places=2,
                                                   max_digits=10)
        self.fields['currency'] = forms.CharField(max_length=3, disabled=True,
                                                  initial=self.payment_request.currency)
        self.fields['description'] = forms.CharField(max_length=50, disabled=True,
                                                     initial=self.payment_request.description, required=False)

    def clean_amount(self):
        declined = self.data.get('request_decline')

        # If the user declined the request, no need to check anything
        if not declined:
            balance = Balance.objects.get(user=self.request.user)

            req_amount, conversion_success = convert_currency(self.payment_request.currency, self.request.user.currency,
                                                              self.payment_request.amount)

            # Handle conversion error
            if not conversion_success:
                raise forms.ValidationError("There was a problem processing your request, please try again.")

            if balance and req_amount > balance.amount:
                raise forms.ValidationError("Insufficient funds to accept this request.")

        return self.cleaned_data.get('amount')


class PaymentRequestForm(forms.ModelForm):
    recipient_email = forms.EmailField(
        label='Request from:',
        widget=forms.TextInput(attrs={'placeholder': 'example@email.com'})
    )

    class Meta:
        model = PaymentRequest
        fields = ['recipient_email', 'amount', 'currency', 'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PaymentRequestForm, self).__init__(*args, **kwargs)

    def clean_recipient_email(self):
        '''
        Make sure the recipient exists and isn't the same as sender
        '''
        email = self.cleaned_data.get('recipient_email')

        # Check if the sender and recipient aren't the same
        if self.request is not None:
            user = self.request.user

            if user is not None:
                sender_email = user.email

                if sender_email == email:
                    raise forms.ValidationError("You can't send a request to yourself")
        else:
            raise forms.ValidationError("There was a problem processing your request, please try again.")

        qs = CustomUser.objects.filter(email=email, is_admin=False).exclude(pk=self.instance.pk)

        if not qs.exists():
            raise forms.ValidationError("A recipient with the given email address doesn't exist")

        return email

    def clean_amount(self):
        '''
        Make sure the amount is not zero and doesn't exceed max transferable amount
        '''

        amount = self.cleaned_data.get('amount')

        if amount <= 0:
            raise forms.ValidationError("The amount must be greater than 0.00")

        if amount > constants.MAX_AMOUNT:
            raise forms.ValidationError(f'The transferred amount cannot exceed {constants.MAX_AMOUNT}')

        return amount

    def save(self, commit=True):
        if self.request is not None:
            user = self.request.user

            if user is not None:
                sender_email = user.email

                if commit:
                    br = PaymentRequest.objects.create(sender_email=sender_email,
                                                       recipient_email=self.cleaned_data.get('recipient_email'),
                                                       currency=self.cleaned_data.get('currency'),
                                                       amount=self.cleaned_data.get('amount'),
                                                       description=self.cleaned_data.get('description'))
                    return br

        raise forms.ValidationError("There was a problem processing your request, please try again.")

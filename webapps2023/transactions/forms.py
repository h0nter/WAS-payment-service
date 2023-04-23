from django import forms
from .models import BalanceTransfer, Balance, PaymentRequest
import transactions.constants as constants
from .utils import convert_currency, round_up_2dp
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

        qs = CustomUser.objects.filter(email=email)

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

                req_amount = Decimal(round_up_2dp(convert_currency(currency, user.currency, amount)))

                if balance and not balance.amount >= req_amount:
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

        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)

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

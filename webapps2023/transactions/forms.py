from django import forms
from .models import BalanceTransfer, Balance
from .constants import Currency
from .utils import convert_currency
from register.models import CustomUser


class BalanceTransferForm(forms.ModelForm):
    recipient_email = forms.EmailField(
        label='Recipient email',
        widget=forms.TextInput(attrs={'placeholder': 'example@email.com'})
    )

    class Meta:
        model = BalanceTransfer
        fields = ['recipient_email', 'amount', 'currency']

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

        if self.request is not None:
            user = self.request.user

            if user is not None:

                balance = Balance.objects.get(user=user)

                currency = self.cleaned_data.get('currency')

                req_amount = convert_currency(currency, user.currency, amount)

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
                                                        amount=self.cleaned_data.get('amount'))
                    return bt

        raise forms.ValidationError("There was a problem processing your request, please try again.")
